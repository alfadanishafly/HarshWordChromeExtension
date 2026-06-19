// content.js
// Chrome Extension Content Script for Hate Speech Detection

(function() {
  'use strict';

  const API_ENDPOINT = 'http://localhost:8000/api/check_hatespeech/';

  /**
   * Extract text content from the page
   * @returns {string} Combined text from body and headings
   */
  function extractPageText() {
    const bodyTextNodes = document.evaluate(
      "//body//text()[not(ancestor::script)][not(ancestor::style)][not(ancestor::textarea)][not(ancestor::option)]",
      document,
      null,
      XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE,
      null
    );

    const headingTextNodes = document.evaluate(
      "//h1|//h2|//h3|//h4|//h5|//h6",
      document,
      null,
      XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE,
      null
    );

    let textContent = '';

    for (let i = 0; i < bodyTextNodes.snapshotLength; i++) {
      textContent += bodyTextNodes.snapshotItem(i).textContent + ' ';
    }

    for (let i = 0; i < headingTextNodes.snapshotLength; i++) {
      textContent += headingTextNodes.snapshotItem(i).textContent + ' ';
    }

    // Clean up text
    textContent = textContent.replace(/[^a-zA-Z0-9\s]/g, ' ');
    textContent = textContent.replace(/\s+/g, ' ').trim();

    return textContent;
  }

  /**
   * Send text to hate speech detection API
   * @param {string} text - Text to analyze
   * @returns {Promise<boolean>} - True if hate speech detected
   */
  async function checkHateSpeech(text) {
    try {
      const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Hate speech detection result:', data);
      return data.is_hatespeech || false;
    } catch (error) {
      console.error('Error checking hate speech:', error);
      return false;
    }
  }

  /**
   * Censor a text node if it contains hate speech
   * @param {Text} node - Text node to check and potentially censor
   */
  async function censorNodeIfHateSpeech(node) {
    const originalText = node.textContent.trim();
    
    if (!originalText) return;

    try {
      const isHateSpeech = await checkHateSpeech(originalText);
      
      if (isHateSpeech) {
        const censoredText = '*'.repeat(originalText.length);
        const newNode = document.createTextNode(censoredText);
        node.parentNode.replaceChild(newNode, node);
        console.log('Censored hate speech content');
      }
    } catch (error) {
      console.error('Error processing node:', error);
    }
  }

  /**
   * Recursively process DOM nodes for hate speech
   * @param {Node} node - Root node to start processing from
   */
  async function processDomNodes(node) {
    if (node.nodeType === Node.TEXT_NODE) {
      const parent = node.parentNode;
      // Skip script and style tags
      if (parent && !['SCRIPT', 'STYLE'].includes(parent.tagName)) {
        await censorNodeIfHateSpeech(node);
      }
    } else if (node.childNodes) {
      for (const child of node.childNodes) {
        await processDomNodes(child);
      }
    }
  }

  /**
   * Main function to process page content
   */
  async function processTextContent() {
    const textContent = extractPageText();
    console.log('Extracted text content:', textContent.substring(0, 100) + '...');

    if (textContent.length > 0) {
      try {
        const isHateSpeech = await checkHateSpeech(textContent);
        
        if (isHateSpeech) {
          console.log('Hate speech detected on page');
          
          // Notify background script
          chrome.runtime.sendMessage({ 
            message: 'hatespeechResult', 
            isHatespeech: true 
          });
          
          // Process and censor content
          await processDomNodes(document.body);
        }
        
        // Always send check message to background
        chrome.runtime.sendMessage({ message: 'checkHatespeech' });
      } catch (error) {
        console.error('Error in main processing:', error);
      }
    }
  }

  // Initialize when page loads
  if (document.readyState === 'loading') {
    window.addEventListener('load', processTextContent);
  } else {
    processTextContent();
  }
})();
