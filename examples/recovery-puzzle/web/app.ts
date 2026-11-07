// SPDX-License-Identifier: MIT
import { Game, boards, type Snapshot } from './engine.js';
const game=new Game();
const get=<T extends HTMLElement>(id: string)=>document.getElementById(id) as T;
const storageKey='paga.switchboard.v1';
let audio: AudioContext | undefined;
function sound(state: Snapshot): void {
 if(state.muted || state.cue==='none') return;
 try {
  audio??=new AudioContext();void audio.resume();
  const osc=audio.createOscillator(),gain=audio.createGain();
  osc.frequency.value=state.cue==='complete'?660:state.cue==='switch'?440:330;
  gain.gain.setValueAtTime(.035,audio.currentTime);gain.gain.exponentialRampToValueAtTime(.001,audio.currentTime+.12);
  osc.connect(gain).connect(audio.destination);osc.start();osc.stop(audio.currentTime+.13);
 } catch {/* A missing output device cannot change gameplay. Listening is a separate gate. */}
}
const errors: Record<string,string>={blocked:'That square is blocked.',not_playing:'Start a campaign or choose a practice board.',nothing_to_undo:'There is no move to undo.',cannot_advance:'Complete a campaign board before advancing.',board_finished:'Board complete. Undo, restart, or advance.',invalid_save:'The save is invalid. Your current game is unchanged.',save_failed:'Saving failed. Your previous save is preserved.'};
function render(state: Snapshot,message?: string): void {
 get('board-label').textContent=`BOARD ${String(state.board).padStart(2,'0')} / 06`;
 get('mode-label').textContent=state.mode.toUpperCase();get('moves').textContent=String(state.moves);
 get('door-state').textContent=state.door?'Door open':'Door closed';
 get('mute').textContent=state.muted?'Sound off':'Sound on';get('mute').setAttribute('aria-pressed',String(state.muted));
 const field=get('board');field.replaceChildren();
 boards[state.board-1].forEach((row,y)=>[...row].forEach((raw,x)=>{
  const cell=raw==='@'?'.':raw,player=x===state.x && y===state.y;
  const tile=document.createElement('button');tile.type='button';tile.tabIndex=-1;
  const desc=player?'Player':cell==='#'?'Wall':cell==='S'?'Switch':cell==='D'?(state.door?'Open door':'Closed door'):cell==='E'?'Exit':'Floor';
  tile.textContent=player?'●':cell==='#'?'':cell==='D'?(state.door?'·':'D'):cell==='.'?'·':cell;
  tile.className=player?'player':cell==='#'?'wall':cell==='S'?'switch':cell==='D'?'door':cell==='E'?'exit':'floor';
  tile.setAttribute('aria-label',`${desc}, column ${x+1}, row ${y+1}`);
  if(cell==='#') tile.disabled=true;
  tile.addEventListener('click',()=>{
   const dx=x-game.x,dy=y-game.y;
   if(Math.abs(dx)+Math.abs(dy)!==1) {get('status').textContent='Choose a square next to the player.';return;}
   dispatch(dx<0?'left':dx>0?'right':dy<0?'up':'down');
  });field.append(tile);
 }));
 const sceneText=state.scene==='title'?'Start a campaign or choose a practice board.':state.scene==='campaign_complete'?'Campaign complete. All six boards are finished.':state.scene==='board_complete'?'Board complete. Choose Next board, Undo, or Restart.':`Board ${state.board}. ${state.door?'Door open.':'Door closed.'} ${state.moves} ${state.moves===1?'move':'moves'}.`;
 get('status').textContent=message??(state.error?(errors[state.error]??state.error):sceneText);
}
function dispatch(action: string): void {const state=game.action(action);render(state);sound(state);}
document.querySelectorAll<HTMLButtonElement>('[data-action]').forEach(b=>b.addEventListener('click',()=>dispatch(b.dataset.action!)));
get('campaign').addEventListener('click',()=>dispatch('new campaign'));
get('practice').addEventListener('click',()=>dispatch(`new practice ${get<HTMLSelectElement>('board-select').value}`));
get('mute').addEventListener('click',()=>dispatch('mute'));
document.addEventListener('keydown',event=>{
 if(event.target instanceof HTMLInputElement || event.target instanceof HTMLSelectElement || event.ctrlKey || event.metaKey || event.altKey) return;
 const action: Record<string,string>={ArrowUp:'up',ArrowDown:'down',ArrowLeft:'left',ArrowRight:'right',u:'undo'};
 if(action[event.key]) {event.preventDefault();dispatch(action[event.key]);}
});
get('save').addEventListener('click',()=>{
 try {
  const text=game.serialize();localStorage.setItem(storageKey+'.pending',text);
  if(new Game().restore(localStorage.getItem(storageKey+'.pending')??'').error) throw Error('readback');
  localStorage.setItem(storageKey,text);localStorage.removeItem(storageKey+'.pending');
  render(game.snapshot(),'Saved in this browser, including undo history.');
 } catch {render(game.snapshot('none','save_failed'));}
});
get('load').addEventListener('click',()=>{
 try {render(game.restore(localStorage.getItem(storageKey)??''));}catch{render(game.snapshot('none','invalid_save'));}
});
get('export').addEventListener('click',()=>{
 const url=URL.createObjectURL(new Blob([game.serialize()],{type:'text/plain'}));
 const link=document.createElement('a');link.href=url;link.download='switchboard-save.txt';link.click();URL.revokeObjectURL(url);
});
get<HTMLInputElement>('import').addEventListener('change',async event=>{
 const input=event.target as HTMLInputElement,file=input.files?.[0];if(!file) return;
 try {render(file.size>=16384?game.snapshot('none','invalid_save'):game.restore(await file.text()));}
 catch {render(game.snapshot('none','invalid_save'));}finally{input.value='';}
});
render(game.snapshot());
