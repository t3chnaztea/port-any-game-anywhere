/* SPDX-License-Identifier: MIT
 * Source-authored translation of the public reference contract. Not recovered.
 */
export const boards = [
 ['#######','#@SD.E#','###.###','#.....#','#######'],
 ['#######','#@S...#','#####D#','#E....#','#######'],
 ['#######','#E.DS@#','###.###','#.....#','#######'],
 ['#######','#@....#','#S###.#','#..D.E#','#######'],
 ['#######','#@S#E.#','#..D..#','#.....#','#######'],
 ['#######','#@S.D.#','#.###.#','#....E#','#######'],
];
type Step = { x: number; y: number; door: boolean; moves: number; scene: number };
export type Snapshot = {
 scene: string; mode: string; board: number; x: number; y: number;
 door: boolean; moves: number; unlocked: number; muted: boolean;
 undo: number; cue: string; error: string | null;
};
const scenes = ['title','playing','board_complete','campaign_complete'];
export class Game {
 mode=0; board=0; scene=0; x=1; y=1; door=false; moves=0;
 unlocked=1; muted=false; history: Step[]=[];
 constructor() { this.begin(0); this.scene=0; }
 private begin(board: number): void {
  this.board=board; this.scene=1; this.door=false; this.moves=0; this.history=[];
  boards[board].forEach((row,y)=>{ const x=row.indexOf('@'); if(x>=0) {this.x=x;this.y=y;} });
 }
 snapshot(cue='none',error: string | null=null): Snapshot {
  return {scene:scenes[this.scene],mode:this.mode?'practice':'campaign',board:this.board+1,
   x:this.x,y:this.y,door:this.door,moves:this.moves,unlocked:this.unlocked,muted:this.muted,
   undo:this.history.length,cue,error};
 }
 action(command: string): Snapshot {
  const fail=(error: string)=>this.snapshot('none',error);
  if(command==='new campaign') {this.mode=0;this.unlocked=1;this.begin(0);return this.snapshot('start');}
  const practice=/^new practice (-?\d+)$/.exec(command);
  if(practice) {
   const b=Number(practice[1]); if(b<1 || b>6) return fail('invalid_board');
   this.mode=1;this.begin(b-1);return this.snapshot('start');
  }
  if(command==='menu') {this.scene=0;this.history=[];return this.snapshot();}
  if(command==='mute') {this.muted=!this.muted;return this.snapshot();}
  if(command==='state') return this.snapshot();
  if(this.scene===0) return fail('not_playing');
  if(command==='restart') {this.begin(this.board);return this.snapshot('start');}
  if(command==='undo') {
   const step=this.history.pop();if(!step) return fail('nothing_to_undo');
   Object.assign(this,step);return this.snapshot();
  }
  if(command==='next') {
   if(this.scene!==2 || this.mode!==0 || this.board>=5) return fail('cannot_advance');
   this.unlocked=Math.max(this.unlocked,this.board+2);this.begin(this.board+1);return this.snapshot('start');
  }
  if(this.scene!==1) return fail('board_finished');
  const delta: Record<string, number[]>={left:[-1,0],right:[1,0],up:[0,-1],down:[0,1]};
  if(!Object.hasOwn(delta,command)) return fail('unknown_action');
  const [dx,dy]=delta[command],x=this.x+dx,y=this.y+dy;
  const cell=boards[this.board][y]?.[x];
  if(!cell || cell==='#' || (cell==='D' && !this.door)) return fail('blocked');
  if(this.moves===1000000) return fail('move_limit');
  this.history.push({x:this.x,y:this.y,door:this.door,moves:this.moves,scene:this.scene});
  if(this.history.length>128) this.history.shift();
  this.x=x;this.y=y;this.moves++;
  let cue='none'; if(cell==='S') {this.door=!this.door;cue='switch';}
  if(cell==='E') {this.scene=this.mode===0 && this.board===5?3:2;cue='complete';}
  return this.snapshot(cue);
 }
 serialize(): string {
  let body=`SB1\n${this.mode} ${this.board} ${this.scene} ${this.x} ${this.y} ${Number(this.door)} ${this.moves} ${this.unlocked} ${Number(this.muted)} ${this.history.length}\n`;
  for(const s of this.history) body+=`${s.x} ${s.y} ${Number(s.door)} ${s.moves} ${s.scene}\n`;
  let h=2166136261;for(const ch of new TextEncoder().encode(body)) h=Math.imul(h^ch,16777619)>>>0;
  return body+`END ${h.toString(16).padStart(8,'0')}\n`;
 }
 restore(text: string): Snapshot {
  const fail=()=>this.snapshot('none','invalid_save');
  if(text.length>=16384 || !/^SB1\n[\s\S]*END [0-9a-f]{8}\n$/.test(text)) return fail();
  const lines=text.split('\n');
  if(!/^-?\d+( -?\d+){9}$/.test(lines[1])) return fail();
  const [mode,board,scene,x,y,door,moves,unlocked,muted,count]=lines[1].split(' ').map(Number);
  if(![0,1].includes(mode) || board<0 || board>5 || unlocked<1 || unlocked>6 || ![0,1].includes(muted) || count<0 || count>128 || lines.length!==count+4) return fail();
  if((mode===0 && board>=unlocked) || moves<count || (scene===0 && count!==0)) return fail();
  const valid=(s: Step)=>{
   if(!Number.isSafeInteger(s.moves) || s.moves<0 || s.moves>1000000 || s.x<0 || s.x>6 || s.y<0 || s.y>4 || s.scene<0 || s.scene>3) return false;
   const cell=boards[board][s.y][s.x];
   return cell!=='#' && !(cell==='D' && !s.door) && (!(s.scene===2 || s.scene===3) || cell==='E') && (s.scene!==3 || (mode===0 && board===5)) && !(s.scene===2 && mode===0 && board===5) && !(s.scene===1 && cell==='E');
  };
  if(![0,1].includes(door) || !valid({x,y,door:!!door,moves,scene})) return fail();
  const history: Step[]=[];
  for(let i=0;i<count;i++) {
   if(!/^-?\d+( -?\d+){4}$/.test(lines[i+2])) return fail();
   const [sx,sy,sd,sm,ss]=lines[i+2].split(' ').map(Number);
   const step={x:sx,y:sy,door:!!sd,moves:sm,scene:ss};
   if(![0,1].includes(sd) || !valid(step) || ss!==1 || sm!==moves-count+i) return fail();history.push(step);
  }
  const candidate=new Game();Object.assign(candidate,{mode,board,scene,x,y,door:!!door,moves,unlocked,muted:!!muted,history});
  if(candidate.serialize()!==text) return fail();
  Object.assign(this,candidate);return this.snapshot();
 }
}
