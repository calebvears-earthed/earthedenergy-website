import { mountInteractive } from "/scripts/dc_engine.mjs";

var root = document.getElementById("ee-app");
var template = document.getElementById("ee-template");
var logic = document.getElementById("ee-logic");
if (root && template && logic) {
  mountInteractive(root, template.innerHTML, logic.textContent);
}
