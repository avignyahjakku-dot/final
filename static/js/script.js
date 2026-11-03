/**
 * =============================================================================
 * Smart Lost & Found System - Client Interactive Script (script.js)
 * Vanilla JavaScript (No Frameworks)
 * Developed for BTech CSE 2-Student Team Project
 * =============================================================================
 */

document.addEventListener("DOMContentLoaded", () => {
  initNavbar();
  initAlerts();
  initImagePreviews();
  initFormValidations();
  if (document.getElementById("dsa-visualizer-app")) {
    initDSAVisualizer();
  }
});

/* --------------------------------------------------------------------------
 * 1. Mobile Navigation
 * -------------------------------------------------------------------------- */
function initNavbar() {
  const toggleBtn = document.querySelector(".nav-toggle");
  const navMenu = document.querySelector(".nav-menu");

  if (toggleBtn && navMenu) {
    toggleBtn.addEventListener("click", () => {
      navMenu.classList.toggle("active");
    });
  }
}

/* --------------------------------------------------------------------------
 * 2. Auto-Dismiss Flash Alerts
 * -------------------------------------------------------------------------- */
function initAlerts() {
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach((alert) => {
    setTimeout(() => {
      alert.style.transition = "opacity 0.5s ease, transform 0.5s ease";
      alert.style.opacity = "0";
      alert.style.transform = "translateY(-10px)";
      setTimeout(() => alert.remove(), 500);
    }, 5000);
  });
}

/* --------------------------------------------------------------------------
 * 3. Image Upload Preview
 * -------------------------------------------------------------------------- */
function initImagePreviews() {
  const fileInputs = document.querySelectorAll('input[type="file"][data-preview]');
  fileInputs.forEach((input) => {
    const previewContainerId = input.getAttribute("data-preview");
    const previewContainer = document.getElementById(previewContainerId);

    if (previewContainer) {
      input.addEventListener("change", function () {
        const file = this.files[0];
        if (file) {
          if (file.size > 5 * 1024 * 1024) {
            alert("File size exceeds 5MB limit. Please choose a smaller image.");
            this.value = "";
            previewContainer.innerHTML = "";
            return;
          }
          const reader = new FileReader();
          reader.onload = function (e) {
            previewContainer.innerHTML = `
              <div style="margin-top: 10px; border-radius: 8px; overflow: hidden; border: 1px solid #cbd5e1; max-width: 200px;">
                <img src="${e.target.result}" alt="Preview" style="width:100%; height:auto; display:block;" />
              </div>
            `;
          };
          reader.readAsDataURL(file);
        } else {
          previewContainer.innerHTML = "";
        }
      });
    }
  });
}

/* --------------------------------------------------------------------------
 * 4. Client-side Form Validation
 * -------------------------------------------------------------------------- */
function initFormValidations() {
  const registerForm = document.querySelector("#register-form");
  if (registerForm) {
    registerForm.addEventListener("submit", function (e) {
      const pw = document.getElementById("password").value;
      const cpw = document.getElementById("confirm_password").value;
      if (pw !== cpw) {
        e.preventDefault();
        alert("Passwords do not match. Please verify.");
      }
    });
  }
}

/* --------------------------------------------------------------------------
 * 5. Full Interactive DSA Visualizer Suite
 * -------------------------------------------------------------------------- */
function initDSAVisualizer() {
  const tabs = document.querySelectorAll(".tab-btn");
  const tabPanels = document.querySelectorAll(".tab-panel");

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      tabs.forEach((t) => t.classList.remove("active"));
      tabPanels.forEach((p) => (p.style.display = "none"));

      tab.classList.add("active");
      const targetPanel = document.getElementById(tab.getAttribute("data-target"));
      if (targetPanel) {
        targetPanel.style.display = "block";
      }

      // Re-render specific visualization if needed
      if (tab.getAttribute("data-target") === "panel-bst") {
        renderBSTCanvas();
      }
    });
  });

  // Setup Visualizer Engines
  setupSortingVisualizer();
  setupSearchingVisualizer();
  setupLinkedListVisualizer();
  setupBSTVisualizer();
}

/* --------------------------------------------------------------------------
 * A. Sorting Visualizer (Bubble, Insertion, Selection)
 * -------------------------------------------------------------------------- */
let sortArray = [45, 12, 85, 32, 89, 39, 69, 21, 55, 76];
let isSorting = false;

function setupSortingVisualizer() {
  const container = document.getElementById("sort-bars-container");
  const algoSelect = document.getElementById("sort-algo-select");
  const btnReset = document.getElementById("btn-sort-reset");
  const btnStart = document.getElementById("btn-sort-start");
  const logBox = document.getElementById("sort-log-box");

  function drawBars(highlight = {}) {
    if (!container) return;
    container.innerHTML = "";
    const maxVal = Math.max(...sortArray, 100);

    sortArray.forEach((val, idx) => {
      const bar = document.createElement("div");
      bar.className = "bar-element";
      bar.style.height = `${(val / maxVal) * 260}px`;
      bar.textContent = val;

      if (highlight.comparing && highlight.comparing.includes(idx)) {
        bar.classList.add("comparing");
      }
      if (highlight.swapping && highlight.swapping.includes(idx)) {
        bar.classList.add("swapping");
      }
      if (highlight.sorted && highlight.sorted.includes(idx)) {
        bar.classList.add("sorted");
      }

      container.appendChild(bar);
    });
  }

  function log(msg) {
    if (logBox) {
      logBox.innerHTML = `<div>&gt; ${msg}</div>` + logBox.innerHTML;
    }
  }

  const delay = (ms) => new Promise((res) => setTimeout(res, ms));

  async function bubbleSort() {
    isSorting = true;
    const n = sortArray.length;
    let comps = 0, swaps = 0;
    log("Started Bubble Sort: Comparing adjacent elements...");

    for (let i = 0; i < n; i++) {
      let swapped = false;
      for (let j = 0; j < n - i - 1; j++) {
        if (!isSorting) return;
        comps++;
        drawBars({ comparing: [j, j + 1] });
        await delay(120);

        if (sortArray[j] > sortArray[j + 1]) {
          drawBars({ swapping: [j, j + 1] });
          await delay(120);
          let temp = sortArray[j];
          sortArray[j] = sortArray[j + 1];
          sortArray[j + 1] = temp;
          swaps++;
          swapped = true;
          drawBars({ swapping: [j, j + 1] });
          await delay(100);
        }
      }
      if (!swapped) break;
    }
    drawBars({ sorted: sortArray.map((_, i) => i) });
    log(`Bubble Sort complete! Total comparisons: ${comps}, Swaps: ${swaps}`);
    isSorting = false;
  }

  async function selectionSort() {
    isSorting = true;
    const n = sortArray.length;
    let comps = 0, swaps = 0;
    log("Started Selection Sort: Searching minimum in unsorted sub-array...");

    for (let i = 0; i < n; i++) {
      let minIdx = i;
      for (let j = i + 1; j < n; j++) {
        if (!isSorting) return;
        comps++;
        drawBars({ comparing: [minIdx, j] });
        await delay(100);
        if (sortArray[j] < sortArray[minIdx]) {
          minIdx = j;
        }
      }
      if (minIdx !== i) {
        drawBars({ swapping: [i, minIdx] });
        await delay(140);
        let temp = sortArray[i];
        sortArray[i] = sortArray[minIdx];
        sortArray[minIdx] = temp;
        swaps++;
      }
    }
    drawBars({ sorted: sortArray.map((_, i) => i) });
    log(`Selection Sort complete! Total comparisons: ${comps}, Swaps: ${swaps}`);
    isSorting = false;
  }

  async function insertionSort() {
    isSorting = true;
    const n = sortArray.length;
    let comps = 0, shifts = 0;
    log("Started Insertion Sort: Shifting items into sorted prefix...");

    for (let i = 1; i < n; i++) {
      let key = sortArray[i];
      let j = i - 1;

      while (j >= 0) {
        if (!isSorting) return;
        comps++;
        drawBars({ comparing: [j, j + 1] });
        await delay(100);

        if (sortArray[j] > key) {
          sortArray[j + 1] = sortArray[j];
          shifts++;
          j--;
          drawBars({ swapping: [j + 1] });
          await delay(80);
        } else {
          break;
        }
      }
      sortArray[j + 1] = key;
    }
    drawBars({ sorted: sortArray.map((_, i) => i) });
    log(`Insertion Sort complete! Total comparisons: ${comps}, Shifts: ${shifts}`);
    isSorting = false;
  }

  if (btnReset) {
    btnReset.addEventListener("click", () => {
      isSorting = false;
      sortArray = Array.from({ length: 10 }, () => Math.floor(Math.random() * 85) + 15);
      drawBars();
      log("Array reset to randomized values.");
    });
  }

  if (btnStart) {
    btnStart.addEventListener("click", () => {
      if (isSorting) return;
      const algo = algoSelect ? algoSelect.value : "bubble";
      if (algo === "selection") selectionSort();
      else if (algo === "insertion") insertionSort();
      else bubbleSort();
    });
  }

  drawBars();
}

/* --------------------------------------------------------------------------
 * B. Searching Visualizer (Linear Search & Binary Search)
 * -------------------------------------------------------------------------- */
function setupSearchingVisualizer() {
  const container = document.getElementById("search-cells-container");
  const btnLinear = document.getElementById("btn-linear-search");
  const btnBinary = document.getElementById("btn-binary-search");
  const targetInput = document.getElementById("search-target-input");
  const logBox = document.getElementById("search-log-box");

  let searchData = [10, 18, 25, 33, 47, 52, 64, 71, 88, 95];

  function renderCells(activeIdx = null, foundIdx = null, range = null) {
    if (!container) return;
    container.innerHTML = "";
    searchData.forEach((val, idx) => {
      const cell = document.createElement("div");
      cell.style.width = "52px";
      cell.style.height = "52px";
      cell.style.borderRadius = "8px";
      cell.style.display = "flex";
      cell.style.flexDirection = "column";
      cell.style.alignItems = "center";
      cell.style.justifyContent = "center";
      cell.style.fontWeight = "bold";
      cell.style.color = "#fff";
      cell.style.background = "#1e293b";
      cell.style.border = "2px solid #334155";
      cell.style.transition = "all 0.2s ease";

      cell.innerHTML = `<span>${val}</span><small style="font-size:10px; color:#94a3b8;">[${idx}]</small>`;

      if (range && (idx < range.low || idx > range.high)) {
        cell.style.opacity = "0.25";
      }

      if (idx === activeIdx) {
        cell.style.background = "#f59e0b";
        cell.style.borderColor = "#fbbf24";
        cell.style.transform = "scale(1.15)";
      }
      if (idx === foundIdx) {
        cell.style.background = "#10b981";
        cell.style.borderColor = "#34d399";
        cell.style.transform = "scale(1.2)";
      }

      container.appendChild(cell);
    });
  }

  function log(msg) {
    if (logBox) {
      logBox.innerHTML = `<div>&gt; ${msg}</div>` + logBox.innerHTML;
    }
  }

  const delay = (ms) => new Promise((res) => setTimeout(res, ms));

  if (btnLinear) {
    btnLinear.addEventListener("click", async () => {
      const target = parseInt(targetInput.value);
      if (isNaN(target)) return alert("Enter target integer");
      log(`Starting Linear Search for target: ${target}`);

      let found = false;
      for (let i = 0; i < searchData.length; i++) {
        renderCells(i);
        log(`Checking index [${i}] -> value: ${searchData[i]}`);
        await delay(300);
        if (searchData[i] === target) {
          renderCells(null, i);
          log(`Found target ${target} at index [${i}]! Total comparisons: ${i + 1}`);
          found = true;
          break;
        }
      }
      if (!found) {
        renderCells();
        log(`Target ${target} NOT found in array after ${searchData.length} comparisons.`);
      }
    });
  }

  if (btnBinary) {
    btnBinary.addEventListener("click", async () => {
      const target = parseInt(targetInput.value);
      if (isNaN(target)) return alert("Enter target integer");
      log(`Starting Binary Search for target: ${target} (Array is pre-sorted)`);

      let low = 0;
      let high = searchData.length - 1;
      let comps = 0;
      let found = false;

      while (low <= high) {
        comps++;
        let mid = Math.floor((low + high) / 2);
        renderCells(mid, null, { low, high });
        log(`Interval [${low}..${high}], Mid: index [${mid}] (val: ${searchData[mid]})`);
        await delay(500);

        if (searchData[mid] === target) {
          renderCells(null, mid);
          log(`Found ${target} at index [${mid}] in ${comps} comparisons! O(log n) efficiency.`);
          found = true;
          break;
        } else if (searchData[mid] < target) {
          log(`${searchData[mid]} < ${target}: Narrowing to RIGHT half.`);
          low = mid + 1;
        } else {
          log(`${searchData[mid]} > ${target}: Narrowing to LEFT half.`);
          high = mid - 1;
        }
      }

      if (!found) {
        renderCells();
        log(`Target ${target} was not found. Total comparisons: ${comps}.`);
      }
    });
  }

  renderCells();
}

/* --------------------------------------------------------------------------
 * C. Singly Linked List Visualizer
 * -------------------------------------------------------------------------- */
function setupLinkedListVisualizer() {
  const container = document.getElementById("ll-nodes-container");
  const valInput = document.getElementById("ll-val-input");
  const btnHead = document.getElementById("btn-ll-insert-head");
  const btnTail = document.getElementById("btn-ll-insert-tail");
  const btnDelete = document.getElementById("btn-ll-delete");
  const logBox = document.getElementById("ll-log-box");

  let list = [
    { id: 1, name: "Dell Laptop" },
    { id: 2, name: "Leather Wallet" },
    { id: 3, name: "Casio Calculator" }
  ];

  function renderList() {
    if (!container) return;
    container.innerHTML = "";

    if (list.length === 0) {
      container.innerHTML = `<div style="color:#94a3b8; font-style:italic;">Linked List is empty (HEAD -> NULL)</div>`;
      return;
    }

    // HEAD indicator
    const headBadge = document.createElement("div");
    headBadge.style.cssText = "background:#8b5cf6; color:#fff; padding:6px 10px; border-radius:6px; font-weight:bold; font-size:12px;";
    headBadge.textContent = "HEAD";
    container.appendChild(headBadge);

    list.forEach((item, idx) => {
      // Arrow
      const arrow = document.createElement("div");
      arrow.style.cssText = "color:#38bdf8; font-size:20px; font-weight:bold;";
      arrow.textContent = "→";
      container.appendChild(arrow);

      // Node Box
      const node = document.createElement("div");
      node.style.cssText = "background:#1e293b; border:2px solid #38bdf8; border-radius:8px; padding:8px 12px; color:#fff; display:flex; gap:8px; align-items:center;";
      node.innerHTML = `
        <div style="background:#0284c7; padding:2px 6px; border-radius:4px; font-size:11px;">#${item.id}</div>
        <div style="font-size:13px; font-weight:600;">${item.name}</div>
        <div style="border-left:1px solid #475569; padding-left:6px; color:#94a3b8; font-size:11px;">next</div>
      `;
      container.appendChild(node);
    });

    const nullArrow = document.createElement("div");
    nullArrow.style.cssText = "color:#38bdf8; font-size:20px; font-weight:bold;";
    nullArrow.textContent = "→";
    container.appendChild(nullArrow);

    const nullBadge = document.createElement("div");
    nullBadge.style.cssText = "background:#ef4444; color:#fff; padding:6px 10px; border-radius:6px; font-weight:bold; font-size:12px;";
    nullBadge.textContent = "NULL";
    container.appendChild(nullBadge);
  }

  function log(msg) {
    if (logBox) logBox.innerHTML = `<div>&gt; ${msg}</div>` + logBox.innerHTML;
  }

  if (btnHead) {
    btnHead.addEventListener("click", () => {
      const name = valInput.value.trim() || `Item #${list.length + 1}`;
      const newId = list.length > 0 ? Math.max(...list.map((x) => x.id)) + 1 : 1;
      list.unshift({ id: newId, name: name });
      log(`Inserted at HEAD in O(1) time: [ID: ${newId}, '${name}']`);
      valInput.value = "";
      renderList();
    });
  }

  if (btnTail) {
    btnTail.addEventListener("click", () => {
      const name = valInput.value.trim() || `Item #${list.length + 1}`;
      const newId = list.length > 0 ? Math.max(...list.map((x) => x.id)) + 1 : 1;
      list.push({ id: newId, name: name });
      log(`Inserted at TAIL: [ID: ${newId}, '${name}']`);
      valInput.value = "";
      renderList();
    });
  }

  if (btnDelete) {
    btnDelete.addEventListener("click", () => {
      if (list.length === 0) return alert("List is empty");
      const removed = list.shift();
      log(`Deleted node from HEAD: [ID: ${removed.id}, '${removed.name}']`);
      renderList();
    });
  }

  renderList();
}

/* --------------------------------------------------------------------------
 * D. Binary Search Tree (BST) Canvas Visualizer
 * -------------------------------------------------------------------------- */
let bstRoot = null;

class CanvasBSTNode {
  constructor(key, name) {
    this.key = key;
    this.name = name;
    this.left = null;
    this.right = null;
  }
}

function insertBST(root, key, name) {
  if (!root) return new CanvasBSTNode(key, name);
  if (key < root.key) {
    root.left = insertBST(root.left, key, name);
  } else if (key > root.key) {
    root.right = insertBST(root.right, key, name);
  }
  return root;
}

function setupBSTVisualizer() {
  const canvas = document.getElementById("bst-canvas");
  const keyInput = document.getElementById("bst-key-input");
  const nameInput = document.getElementById("bst-name-input");
  const btnInsert = document.getElementById("btn-bst-insert");
  const btnSearch = document.getElementById("btn-bst-search");
  const btnInorder = document.getElementById("btn-bst-inorder");
  const logBox = document.getElementById("bst-log-box");

  // Seed sample tree
  [50, 30, 70, 20, 40, 60, 80].forEach((k) => {
    bstRoot = insertBST(bstRoot, k, `Report #${k}`);
  });

  function log(msg) {
    if (logBox) logBox.innerHTML = `<div>&gt; ${msg}</div>` + logBox.innerHTML;
  }

  window.renderBSTCanvas = function (highlightKey = null) {
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    function drawNode(node, x, y, dx) {
      if (!node) return;

      // Draw branches
      if (node.left) {
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x - dx, y + 60);
        ctx.strokeStyle = "#475569";
        ctx.lineWidth = 2;
        ctx.stroke();
        drawNode(node.left, x - dx, y + 60, dx / 1.8);
      }

      if (node.right) {
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x + dx, y + 60);
        ctx.strokeStyle = "#475569";
        ctx.lineWidth = 2;
        ctx.stroke();
        drawNode(node.right, x + dx, y + 60, dx / 1.8);
      }

      // Draw node circle
      ctx.beginPath();
      ctx.arc(x, y, 22, 0, 2 * Math.PI);
      if (highlightKey === node.key) {
        ctx.fillStyle = "#f59e0b"; // Yellow highlight
        ctx.strokeStyle = "#fbbf24";
      } else {
        ctx.fillStyle = "#2563eb"; // Blue
        ctx.strokeStyle = "#60a5fa";
      }
      ctx.lineWidth = 3;
      ctx.fill();
      ctx.stroke();

      // Node key text
      ctx.fillStyle = "#ffffff";
      ctx.font = "bold 13px Inter, sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(node.key, x, y);
    }

    drawNode(bstRoot, canvas.width / 2, 45, canvas.width / 4.2);
  };

  if (btnInsert) {
    btnInsert.addEventListener("click", () => {
      const k = parseInt(keyInput.value);
      const name = nameInput.value.trim() || `Item #${k}`;
      if (isNaN(k)) return alert("Enter integer item ID");
      bstRoot = insertBST(bstRoot, k, name);
      log(`Inserted Item ID #${k} ('${name}') into BST in O(log n) average time.`);
      keyInput.value = "";
      nameInput.value = "";
      renderBSTCanvas();
    });
  }

  if (btnSearch) {
    btnSearch.addEventListener("click", async () => {
      const k = parseInt(keyInput.value);
      if (isNaN(k)) return alert("Enter item ID to search");
      log(`Searching BST for Item ID #${k}...`);

      let curr = bstRoot;
      let path = [];
      let found = false;

      while (curr) {
        path.push(curr.key);
        renderBSTCanvas(curr.key);
        await new Promise((r) => setTimeout(r, 450));

        if (k === curr.key) {
          found = true;
          log(`FOUND Item ID #${k}! Traversed path: [${path.join(" -> ")}].`);
          break;
        } else if (k < curr.key) {
          curr = curr.left;
        } else {
          curr = curr.right;
        }
      }

      if (!found) {
        renderBSTCanvas();
        log(`Item ID #${k} does NOT exist in BST. Traversed: [${path.join(" -> ")}].`);
      }
    });
  }

  if (btnInorder) {
    btnInorder.addEventListener("click", () => {
      const traversal = [];
      function inorder(node) {
        if (node) {
          inorder(node.left);
          traversal.push(node.key);
          inorder(node.right);
        }
      }
      inorder(bstRoot);
      log(`BST Inorder Traversal (Left -> Root -> Right): [${traversal.join(", ")}]. Always yields sorted order!`);
    });
  }

  renderBSTCanvas();
}
