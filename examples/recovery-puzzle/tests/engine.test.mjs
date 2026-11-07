// SPDX-License-Identifier: MIT
import test from 'node:test';
import assert from 'node:assert/strict';
import { Game } from '../web/engine.ts';
test('a damaged save cannot replace the current state',()=>{
 const game=new Game();game.action('new campaign');game.action('right');
 const before=game.serialize();const result=game.restore(before.replace('SB1','SB2'));
 assert.equal(result.error,'invalid_save');assert.equal(game.serialize(),before);
});
test('completion is reversible through ordinary undo',()=>{
 const game=new Game();game.action('new campaign');
 for(let i=0;i<4;i++) game.action('right');
 assert.equal(game.snapshot().scene,'board_complete');
 assert.equal(game.action('undo').scene,'playing');
 assert.equal(game.snapshot().moves,3);
});
test('save and cold restore retain all bounded undo steps',()=>{
 const game=new Game();game.action('new campaign');game.action('right');game.action('right');
 const restored=new Game();assert.equal(restored.restore(game.serialize()).error,null);
 assert.equal(restored.action('undo').moves,1);assert.equal(restored.action('undo').moves,0);
});
