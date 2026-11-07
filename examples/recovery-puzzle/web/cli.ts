// SPDX-License-Identifier: MIT
// Node protocol adapter. It uses the same normal actions as the browser.
import { createInterface } from 'node:readline';
import { readFileSync, writeFileSync, renameSync, unlinkSync, openSync, closeSync, fsyncSync } from 'node:fs';
import { Game } from './engine.ts';
const game=new Game();
console.log(JSON.stringify(game.snapshot()));
for await(const line of createInterface({input:process.stdin,crlfDelay:Infinity})) {
 if(line==='quit') break;
 let state;
 if(line.startsWith('load ')) {
  try {state=game.restore(readFileSync(line.slice(5),'utf8'));} catch {state=game.snapshot('none','invalid_save');}
 } else if(line.startsWith('save ')) {
  const path=line.slice(5),temp=path+'.tmp';let owned=false;
  try {
   const fd=openSync(temp,'wx',0o600);owned=true;
   try {writeFileSync(fd,game.serialize());fsyncSync(fd);} finally {closeSync(fd);}
   if(new Game().restore(readFileSync(temp,'utf8')).error) throw Error('readback');
   renameSync(temp,path);owned=false;state=game.snapshot();
  } catch {if(owned) {try {unlinkSync(temp);}catch {}}state=game.snapshot('none','save_failed');}
 } else state=game.action(line);
 console.log(JSON.stringify(state));
}
