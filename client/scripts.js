const GPTResearcher = (() => {

  const startResearch = () => {
      clearOutput();
      listenToSockEvents();
  };

  const clearOutput = () => {
      document.getElementById("output").innerHTML = "";
      document.getElementById("reportContainer").innerHTML = "";
  };

  const listenToSockEvents = () => {
      const { protocol, host, pathname } = window.location;
      const ws_uri = `${protocol === 'https:' ? 'wss:' : 'ws:'}//${host}${pathname}ws`;
      const converter = new showdown.Converter();
      const socket = new WebSocket(ws_uri);

      socket.onmessage = handleSockMessage.bind(null, converter);
      socket.onopen = sendRequestData;
  };

  const handleSockMessage = (converter, event) => {
      const data = JSON.parse(event.data);

      switch (data.type) {
          case 'logs':
              // Mostramos el mensaje "Thinking..." solo si la clave API es válida
              if (data.output === "La clave API es válida") {
                  addAgentResponse({ output: "🤔 Pensando en preguntas de investigación para la tarea..." });
              } else {
                  addAgentResponse(data);
              }
              break;
          case 'report':
              writeReport(data, converter);
              break;
          case 'path':
              updateDownloadLink(data);
              break;
          case 'error':
              showErrorModal(data.output);
              break;
          default:
              console.error("Error no manejado:", data.type);
      }
  };

  const showErrorModal = (message) => {
      const modalBody = document.querySelector('#errorModal .modal-body');
      modalBody.textContent = message;
      
      const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
      errorModal.show();
  };

  const sendRequestData = (event) => {
      const task = document.querySelector('input[name="task"]').value;
      const report_type = document.querySelector('select[name="report_type"]').value;
      const agent = document.querySelector('input[name="agent"]:checked').value;
      const language = document.getElementById("language").value;
      const apiKey = document.getElementById("openai-api-key").value;

      const requestData = {
          task,
          report_type,
          agent,
          language,
          openai_api_key: apiKey
      };

      event.target.send(`start ${JSON.stringify(requestData)}`);
  };

  const addAgentResponse = (data) => {
      const output = document.getElementById("output");
      output.innerHTML += '<div class="agent_response">' + data.output + '</div>';
      output.scrollTop = output.scrollHeight;
      output.style.display = "block";
      updateScroll();
  };

  const writeReport = (data, converter) => {
      const reportContainer = document.getElementById("reportContainer");
      const markdownOutput = converter.makeHtml(data.output);
      reportContainer.innerHTML += markdownOutput;
      updateScroll();
  };

  const updateDownloadLink = (data) => {
      const path = data.output;
      const downloadLink = document.getElementById("downloadLink");
      downloadLink.href = path;
  };

  const updateScroll = () => {
      window.scrollTo(0, document.body.scrollHeight);
  };

  const copyToClipboard = () => {
      const textarea = document.createElement('textarea');
      textarea.id = 'temp_element';
      textarea.style.height = 0;
      document.body.appendChild(textarea);
      textarea.value = document.getElementById('reportContainer').innerText;
      const selector = document.querySelector('#temp_element');
      selector.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
  };

  return {
      startResearch,
      copyToClipboard,
  };

})();




