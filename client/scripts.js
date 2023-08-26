/**
 * GPTResearcher es un módulo que gestiona la comunicación WebSocket 
 * y actualiza la interfaz de usuario según los mensajes del servidor.
 */
const GPTResearcher = (() => {
  // Referencias de elementos DOM
  const outputElement = document.getElementById("output");
  const reportContainerElement = document.getElementById("reportContainer");
  const downloadLinkElement = document.getElementById("downloadLink");

  // Convertidor para transformar markdown en HTML
  const converter = new showdown.Converter();

  // Variables de estado
  let socket;
  let reconnectAttempts = 0;
  const maxReconnectAttempts = 5;

  const startResearch = () => {
      // Inicialización
      outputElement.innerHTML = "";
      reportContainerElement.innerHTML = "";

      addAgentResponse("🤔 Pensando en las preguntas de investigación para la tarea...");
      listenToSockEvents();
  };

  const showError = (message) => {
      alert(message);
  };

  const listenToSockEvents = () => {
      const ws_uri = getWebSocketURI();
      socket = new WebSocket(ws_uri);

      socket.onopen = handleSocketOpen;
      socket.onmessage = handleSocketMessage;
      socket.onerror = handleSocketError;
      socket.onclose = handleSocketClose;
  };

  const getWebSocketURI = () => {
      const { protocol, host, pathname } = window.location;
      return `${protocol === 'https:' ? 'wss:' : 'ws:'}//${host}${pathname}ws`;
  };

  const handleSocketOpen = () => {
      reconnectAttempts = 0;
      initiateSocketCommunication();
  };

  const handleSocketError = (error) => {
      showError("WebSocket Error");
      console.log("WebSocket Error:", error);
  };

  const handleSocketClose = (event) => {
      if (!event.wasClean && reconnectAttempts < maxReconnectAttempts) {
          reconnectAttempts++;
          setTimeout(listenToSockEvents, 2000);
      }
  };

  const initiateSocketCommunication = () => {
      const requestData = gatherFormData();

      console.log("Sending data to server:", requestData);
      if (!requestData.openai_api_key) {
          console.warn("Warning: API key is missing or empty.");
      }

      socket.send(`start ${JSON.stringify(requestData)}`);
  };

  const gatherFormData = () => {
      return {
          task: document.querySelector('input[name="task"]').value,
          report_type: document.querySelector('select[name="report_type"]').value,
          agent: document.querySelector('input[name="agent"]:checked').value,
          language: document.getElementById("language").value,
          openai_api_key: document.getElementById("openai-api-key").value
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

      // Esta es la parte nueva:
      const API = {
        startResearch,
        copyToClipboard
    };

    window.GPTResearcher = API;  // Esto expone GPTResearcher al objeto global window
    
    return API;  // Esto sigue devolviendo las funciones como antes
})();



