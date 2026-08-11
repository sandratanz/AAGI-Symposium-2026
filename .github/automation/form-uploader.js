function processFormSubmission(e) {
  // 1. Fetch the latest configuration from this GitHub repo
  const config = getGitHubConfig();
  
  // 2. Extract the submitted items
  const itemResponses = e.response.getItemResponses();
  
  itemResponses.forEach(itemResponse => {
    const itemType = itemResponse.getItem().getType();
    
    // Process only File Upload fields
    if (itemType == FormApp.ItemType.FILE_UPLOAD) {
      const fileIds = itemResponse.getResponse(); 
      
      fileIds.forEach(fileId => {
        const file = DriveApp.getFileById(fileId);
        
        // Ensure we are processing a PDF
        if (file.getMimeType() === "application/pdf") {
          uploadPdfToGitHub(file, config);
        }
      });
    }
  });
}

function uploadPdfToGitHub(file, config) {
  const blob = file.getBlob();
  const base64Content = Utilities.base64Encode(blob.getBytes());
  const fileName = file.getName();
  
  // Script fetches the secure token from Google's environment properties
  const githubToken = PropertiesService.getScriptProperties().getProperty('GITHUB_TOKEN');
  
  const path = config.UPLOAD_FOLDER_PATH + "/" + fileName; 
  const url = `https://github.com{config.REPO_OWNER}/${config.REPO_NAME}/contents/${path}`;
  
  const payload = {
    "message": "Form Upload: Added " + fileName,
    "content": base64Content,
    "branch": config.BRANCH
  };
  
  const options = {
    "method": "PUT",
    "headers": {
      "Authorization": "Bearer " + githubToken,
      "Content-Type": "application/json",
      "Accept": "application/vnd.github+json"
    },
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };
  
  const response = UrlFetchApp.fetch(url, options);
  Logger.log("GitHub API Response: " + response.getContentText());
}