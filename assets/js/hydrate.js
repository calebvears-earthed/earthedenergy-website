import { mountInteractive } from "/scripts/dc_engine.mjs";

var root = document.getElementById("ee-app");
var template = document.getElementById("ee-template");
var logic = document.getElementById("ee-logic");
if (root && template && logic) {
  try {
    mountInteractive(root, template.innerHTML, logic.textContent);
  } catch (error) {
    console.error("ee calculator", error);
    var note = document.createElement("p");
    note.setAttribute("role", "alert");
    note.style.cssText = "margin:16px;padding:14px 16px;border-radius:10px;background:#2b1550;color:#F5F1E8;font:600 15px/1.45 'Open Sans',sans-serif";
    note.textContent = "The calculator did not start. Call 0433 839 284 or use the contact page.";
    root.prepend(note);
  }
}
