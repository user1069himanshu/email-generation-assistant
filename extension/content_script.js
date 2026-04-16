/**
 * content_script.js — runs on mail.google.com
 *
 * Listens for INSERT_EMAIL messages from popup.js and injects
 * the generated email text into the active Gmail compose box.
 */

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.action !== "INSERT_EMAIL") return;

  // Gmail's compose body uses a contenteditable div with role="textbox"
  const composeBox = document.querySelector(
    'div[role="textbox"][aria-label*="compose"], ' +
    'div[role="textbox"][aria-label*="message body"], ' +
    'div[g_editable="true"]'
  );

  if (!composeBox) {
    sendResponse({ success: false, error: "No compose box found." });
    return;
  }

  // Focus the box first
  composeBox.focus();

  // Clear placeholder text if empty, then set content
  composeBox.innerHTML = "";
  const lines = message.text.split("\n");
  lines.forEach((line, i) => {
    if (i > 0) composeBox.appendChild(document.createElement("br"));
    composeBox.appendChild(document.createTextNode(line));
  });

  // Dispatch input event so Gmail registers the change
  composeBox.dispatchEvent(new InputEvent("input", { bubbles: true }));

  sendResponse({ success: true });
});
