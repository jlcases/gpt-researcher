const GPTResearcher = (() => {
  const outputElement = document.getElementById("output");
  const reportContainerElement = document.getElementById("reportContainer");
  const downloadLinkElement = document.getElementById("downloadLink");
  const converter = new showdown.Converter();

  let socket;
  let reconnectAttempts = 0;
  const maxReconnectAttempts = 5;  // Establece un límite de reintentos

  const startResearch = () => {
      outputElement.innerHTML = "";
      reportContainerElement.innerHTML = "";

      addAgentResponse("🤔 Thinking about research questions for the task...");
      listenToSockEvents();
  };

  const showError = (message) => {
      alert(message);
  };

  const listenToSockEvents = () => {
      const { protocol, host, pathname } = window.location;
      const ws_uri = `${protocol === 'https:' ? 'wss:' : 'ws:'}//${host}${pathname}ws`;
      socket = new WebSocket(ws_uri);

      socket.onopen = () => {
          reconnectAttempts = 0;  // Reset the reconnect attempts
          initiateSocketCommunication();
      };
      socket.onmessage = handleSocketMessage;
      socket.onerror = (error) => {
          showError("WebSocket Error");
          console.log("WebSocket Error:", error);
      };
      socket.onclose = (event) => {
          if (!event.wasClean && reconnectAttempts < maxReconnectAttempts) {
              reconnectAttempts++;
              setTimeout(listenToSockEvents, 2000);
          }
      };
  };

  const handleSocketMessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("Mensaje recibido del servidor:", data);

      switch(data.type) {
          case 'logs':
              addAgentResponse(data.output);
              break;
          case 'report':
              writeReport(data.output);
              break;
          case 'path':
              updateDownloadLink(data.output);
              break;
          case 'error':
              handleServerError(data.output || "Error desconocido desde el servidor.");
              break;
      }
  };

  const initiateSocketCommunication = () => {
      const task = document.querySelector('input[name="task"]').value;
      const report_type = document.querySelector('select[name="report_type"]').value;
      const agent = document.querySelector('input[name="agent"]:checked').value;
      const language = document.getElementById("language").value;
      const openai_api_key = document.getElementById("openai-api-key").value;

      const requestData = {
          task,
          report_type,
          agent,
          language,
          openai_api_key
      };

      console.log("Sending data to server:", requestData);
      if (!openai_api_key) {
          console.warn("Warning: API key is missing or empty.");
      }

      socket.send(`start ${JSON.stringify(requestData)}`);
  };

  const addAgentResponse = (message) => {
      appendMessageToElement(outputElement, message, "agent_response");
  };

  const handleServerError = (errorMessage) => {
      appendMessageToElement(outputElement, errorMessage, "server_error");
  };

  const writeReport = (report) => {
      const markdownOutput = converter.makeHtml(report);
      reportContainerElement.innerHTML += markdownOutput;
      updateScroll();
  };

  const updateDownloadLink = (path) => {
      downloadLinkElement.href = path;
  };

  const appendMessageToElement = (element, message, className) => {
      element.innerHTML += `<div class="${className}">${message}</div>`;
      element.scrollTop = element.scrollHeight;
      element.style.display = "block";
      updateScroll();
  };

  const updateScroll = () => {
      window.scrollTo(0, document.body.scrollHeight);
  };

  const copyToClipboard = () => {
      const textarea = document.createElement('textarea');
      textarea.id = 'temp_element';
      document.body.appendChild(textarea);
      textarea.value = reportContainerElement.innerText;
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
  };

  window.addEventListener('beforeunload', () => {
      if (socket) {
          socket.close();
      }
  });

  return {
      startResearch,
      copyToClipboard
  };
})();


