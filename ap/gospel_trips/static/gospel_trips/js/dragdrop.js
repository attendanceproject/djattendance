// https://codepen.io/dlrbhml/pen/OwPwXY
var dragSrcEl = null;
const MOVE = "move";
const DRAGELEM = "dragElem";
const OVER = "over";

function handleDragStart(e) {
  // Target (this) element is the source node.
  dragSrcEl = this;

  e.dataTransfer.effectAllowed = MOVE;
  e.dataTransfer.setData("text/html", this.outerHTML);

  this.classList.add(DRAGELEM);
}
function handleDragOver(e) {
  if (e.preventDefault) {
    e.preventDefault(); // Necessary. Allows us to drop.
  }
  this.classList.add(OVER);

  e.dataTransfer.dropEffect = MOVE;  // See the section on the DataTransfer object.

  return false;
}

function handleDragEnter(e) {
  // this / e.target is the current hover target.
}

function handleDragLeave(e) {
  this.classList.remove(OVER);  // this / e.target is previous target element.
}

function handleDrop(e) {
  // this/e.target is current target element.

  if (e.stopPropagation) {
    e.stopPropagation(); // Stops some browsers from redirecting.
  }

  // Don't do anything if dropping the same column we're dragging.
  if (dragSrcEl != this) {
    // Set the source column's HTML to the HTML of the column we dropped on.
    this.parentNode.removeChild(dragSrcEl);
    var dropHTML = e.dataTransfer.getData("text/html");
    this.insertAdjacentHTML("beforebegin", dropHTML);
    var dropElem = this.previousSibling;
    addDnDHandlers(dropElem);

  }
  this.classList.remove(OVER);
  return false;
}

function handleDragEnd(e) {
  // this/e.target is the source node.
  this.classList.remove(OVER);

}

function addDnDHandlers(elem) {
  elem.addEventListener("dragstart", handleDragStart, false);
  elem.addEventListener("dragenter", handleDragEnter, false)
  elem.addEventListener("dragover", handleDragOver, false);
  elem.addEventListener("dragleave", handleDragLeave, false);
  elem.addEventListener("drop", handleDrop, false);
  elem.addEventListener("dragend", handleDragEnd, false);

}
