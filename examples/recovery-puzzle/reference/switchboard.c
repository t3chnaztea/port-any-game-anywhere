/* SPDX-License-Identifier: MIT
 * Original Switchboard reference. Source-authored, NOT recovered code.
 * Line commands are the normal interface; --protocol emits JSON only.
 */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

#define HISTORY 128
#define CAPACITY 16384
static const char *boards[6][5] = {
 {"#######", "#@SD.E#", "###.###", "#.....#", "#######"},
 {"#######", "#@S...#", "#####D#", "#E....#", "#######"},
 {"#######", "#E.DS@#", "###.###", "#.....#", "#######"},
 {"#######", "#@....#", "#S###.#", "#..D.E#", "#######"},
 {"#######", "#@S#E.#", "#..D..#", "#.....#", "#######"},
 {"#######", "#@S.D.#", "#.###.#", "#....E#", "#######"}
};
/* Scenes: 0 title, 1 playing, 2 board complete, 3 campaign complete. */
typedef struct { int x, y, door, moves, scene; } Step;
typedef struct {
 int mode, board, scene, x, y, door, moves, unlocked, muted, count;
 Step history[HISTORY];
} Game;
static const char *scene_names[] = {"title", "playing", "board_complete", "campaign_complete"};

static void begin(Game *g, int board) {
 g->board=board; g->scene=1; g->door=0; g->moves=0; g->count=0;
 for(int y=0;y<5;y++) for(int x=0;x<7;x++)
  if(boards[board][y][x]=='@') { g->x=x; g->y=y; }
}
static void initial(Game *g) { memset(g,0,sizeof(*g)); g->unlocked=1; begin(g,0); g->scene=0; }
static uint32_t checksum(const char *text, size_t len) {
 uint32_t h=2166136261u;
 for(size_t i=0;i<len;i++) { h^=(unsigned char)text[i]; h*=16777619u; }
 return h;
}
static int encode(const Game *g,char *out,size_t cap) {
 int n=snprintf(out,cap,"SB1\n%d %d %d %d %d %d %d %d %d %d\n",
  g->mode,g->board,g->scene,g->x,g->y,g->door,g->moves,g->unlocked,g->muted,g->count);
 if(n<0 || (size_t)n>=cap) return 0;
 for(int i=0;i<g->count;i++) {
  Step s=g->history[i]; int w=snprintf(out+n,cap-(size_t)n,"%d %d %d %d %d\n",s.x,s.y,s.door,s.moves,s.scene);
  if(w<0 || (size_t)w>=cap-(size_t)n) return 0;
  n+=w;
 }
 uint32_t hash=checksum(out,(size_t)n);
 int w=snprintf(out+n,cap-(size_t)n,"END %08x\n",hash);
 return w>0 && (size_t)w<cap-(size_t)n;
}
static int valid_step(const Game *g,Step s) {
 if(s.x<0 || s.x>=7 || s.y<0 || s.y>=5 || s.door<0 || s.door>1 || s.moves<0 || s.moves>1000000 || s.scene<0 || s.scene>3) return 0;
 char cell=boards[g->board][s.y][s.x];
 if(cell=='#' || (cell=='D' && !s.door)) return 0;
 if((s.scene==2 || s.scene==3) && cell!='E') return 0;
 if(s.scene==3 && (g->mode!=0 || g->board!=5)) return 0;
 if(s.scene==2 && g->mode==0 && g->board==5) return 0;
 if(s.scene==1 && cell=='E') return 0;
 return 1;
}
static int decode(const char *text,Game *out) {
 size_t len=strlen(text); if(len>=CAPACITY || strncmp(text,"SB1\n",4)!=0) return 0;
 char copy[CAPACITY], canonical[CAPACITY]; memcpy(copy,text,len+1);
 char *cursor=NULL, *line=strtok_r(copy,"\n",&cursor); (void)line;
 line=strtok_r(NULL,"\n",&cursor); if(!line) return 0;
 Game g={0}; int end=0;
 if(sscanf(line,"%d %d %d %d %d %d %d %d %d %d%n",&g.mode,&g.board,&g.scene,&g.x,&g.y,&g.door,&g.moves,&g.unlocked,&g.muted,&g.count,&end)!=10 || line[end]) return 0;
 if(g.mode<0 || g.mode>1 || g.board<0 || g.board>5 || g.unlocked<1 || g.unlocked>6 || g.muted<0 || g.muted>1 || g.count<0 || g.count>HISTORY) return 0;
 if((g.mode==0 && g.board>=g.unlocked) || g.moves<g.count || (g.scene==0 && g.count)) return 0;
 Step now={g.x,g.y,g.door,g.moves,g.scene}; if(!valid_step(&g,now)) return 0;
 for(int i=0;i<g.count;i++) {
  line=strtok_r(NULL,"\n",&cursor); if(!line) return 0;
  Step *s=&g.history[i]; end=0;
  if(sscanf(line,"%d %d %d %d %d%n",&s->x,&s->y,&s->door,&s->moves,&s->scene,&end)!=5 || line[end] || !valid_step(&g,*s) || s->scene!=1 || s->moves!=g.moves-g.count+i) return 0;
 }
 line=strtok_r(NULL,"\n",&cursor); if(!line || strncmp(line,"END ",4)!=0 || strtok_r(NULL,"\n",&cursor)) return 0;
 if(!encode(&g,canonical,sizeof canonical) || strcmp(canonical,text)) return 0;
 *out=g; return 1;
}
static int load_file(const char *path,Game *out) {
 FILE *f=fopen(path,"rb"); if(!f) return 0;
 char data[CAPACITY]; size_t n=fread(data,1,sizeof(data)-1,f); int extra=fgetc(f);
 int bad=ferror(f); fclose(f); data[n]=0;
 if(bad || extra!=EOF || memchr(data,0,n)) return 0;
 return decode(data,out);
}
static int save_file(const char *path,const Game *g) {
 char data[CAPACITY], temporary[4096];
 if(!*path || !encode(g,data,sizeof data) || snprintf(temporary,sizeof temporary,"%s.tmp",path)>=(int)sizeof temporary) return 0;
 int fd=open(temporary,O_WRONLY|O_CREAT|O_EXCL,0600); if(fd<0) return 0;
 size_t len=strlen(data),done=0; int ok=1;
 while(done<len) { ssize_t n=write(fd,data+done,len-done); if(n<=0) {ok=0;break;} done+=(size_t)n; }
 if(ok && fsync(fd)!=0) ok=0;
 if(close(fd)!=0) ok=0;
 Game checked;
 if(ok && !load_file(temporary,&checked)) ok=0;
 if(ok && rename(temporary,path)!=0) ok=0;
 if(!ok) unlink(temporary); /* Only the temporary file this invocation created. */
 return ok;
}
static void remember(Game *g) {
 if(g->count==HISTORY) { memmove(g->history,g->history+1,(HISTORY-1)*sizeof(Step)); g->count--; }
 g->history[g->count++]=(Step){g->x,g->y,g->door,g->moves,g->scene};
}
static const char *act(Game *g,const char *line,const char **cue) {
 *cue="none";
 if(!strcmp(line,"new campaign")) {g->mode=0;g->unlocked=1;begin(g,0);*cue="start";return NULL;}
 int b=0,n=0;
 if(sscanf(line,"new practice %d%n",&b,&n)==1 && !line[n]) {
  if(b<1 || b>6) return "invalid_board";
  g->mode=1;begin(g,b-1);*cue="start";return NULL;
 }
 if(!strcmp(line,"menu")) {g->scene=0;g->count=0;return NULL;}
 if(!strcmp(line,"mute")) {g->muted=!g->muted;return NULL;}
 if(!strncmp(line,"save ",5)) return save_file(line+5,g) ? NULL : "save_failed";
 if(!strncmp(line,"load ",5)) {Game saved; if(!load_file(line+5,&saved)) return "invalid_save";*g=saved;return NULL;}
 if(!strcmp(line,"state")) return NULL;
 if(g->scene==0) return "not_playing";
 if(!strcmp(line,"restart")) {begin(g,g->board);*cue="start";return NULL;}
 if(!strcmp(line,"undo")) {
  if(!g->count) return "nothing_to_undo";
  Step s=g->history[--g->count];g->x=s.x;g->y=s.y;g->door=s.door;g->moves=s.moves;g->scene=s.scene;return NULL;
 }
 if(!strcmp(line,"next")) {
  if(g->scene!=2 || g->mode!=0 || g->board>=5) return "cannot_advance";
  int next=g->board+1; if(g->unlocked<next+1) g->unlocked=next+1;
  begin(g,next);*cue="start";return NULL;
 }
 if(g->scene!=1) return "board_finished";
 int dx=0,dy=0;
 if(!strcmp(line,"left")) dx=-1; else if(!strcmp(line,"right")) dx=1;
 else if(!strcmp(line,"up")) dy=-1; else if(!strcmp(line,"down")) dy=1; else return "unknown_action";
 int x=g->x+dx,y=g->y+dy;
 if(x<0 || x>=7 || y<0 || y>=5) return "blocked";
 char cell=boards[g->board][y][x]; if(cell=='#' || (cell=='D' && !g->door)) return "blocked";
 if(g->moves==1000000) return "move_limit";
 remember(g);g->x=x;g->y=y;g->moves++;
 if(cell=='S') {g->door=!g->door;*cue="switch";}
 if(cell=='E') {g->scene=(g->mode==0 && g->board==5)?3:2;*cue="complete";}
 return NULL;
}
static void print_json(const Game *g,const char *cue,const char *error) {
 printf("{\"scene\":\"%s\",\"mode\":\"%s\",\"board\":%d,\"x\":%d,\"y\":%d,\"door\":%s,\"moves\":%d,\"unlocked\":%d,\"muted\":%s,\"undo\":%d,\"cue\":\"%s\",\"error\":",
  scene_names[g->scene],g->mode?"practice":"campaign",g->board+1,g->x,g->y,g->door?"true":"false",g->moves,g->unlocked,g->muted?"true":"false",g->count,cue);
 if(error) printf("\"%s\"",error);else printf("null");
 puts("}");fflush(stdout);
}
static void display(const Game *g) {
 for(int y=0;y<5;y++) {for(int x=0;x<7;x++) {
  char c=boards[g->board][y][x];if(c=='@') c='.';if(c=='D' && g->door) c='.';if(x==g->x && y==g->y) c='@';putchar(c);
 }putchar('\n');}
}
int main(int argc,char **argv) {
 int protocol=(argc==2 && !strcmp(argv[1],"--protocol"));
 if(argc>1 && !protocol) {fputs("Usage: switchboard [--protocol]\n",stderr);return 2;}
 Game g;initial(&g);
 if(!protocol) puts("Switchboard: new campaign | new practice 1..6 | up/down/left/right | undo | restart | next | menu | mute | save PATH | load PATH | quit");
 print_json(&g,"none",NULL);char line[4096];
 while(fgets(line,sizeof line,stdin)) {
  size_t len=strlen(line);if(len && line[len-1]=='\n') line[--len]=0;
  if(len && line[len-1]=='\r') line[--len]=0;
  if(!strcmp(line,"quit")) break;
  const char *cue,*error=act(&g,line,&cue);
  if(!protocol) {if(!g.muted && strcmp(cue,"none")) putchar('\a');display(&g);}
  print_json(&g,cue,error);
 }
 return ferror(stdin)?1:0;
}
