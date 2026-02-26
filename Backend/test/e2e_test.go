package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"
	"time"
)

const baseURL = "http://localhost:8080/api/v1"

func main() {
	fmt.Println("=== Starting E2E Backend Test ===")

	timestamp := time.Now().Unix()
	username := fmt.Sprintf("testuser_%d", timestamp)
	password := "securepassword123"

	fmt.Printf("\n[*] Registering user: %s\n", username)
	register(username, password)

	fmt.Println("\n[*] Logging in...")
	token := login(username, password)
	if token == "" {
		fmt.Println("[X] Aborting test due to login failure.")
		return
	}
	fmt.Printf("    -> Received JWT Token: %s...\n", token[:20])

	fmt.Println("\n[*] Fetching history...")
	history(token)

	fmt.Println("\n[*] Sending real files to /detect endpoint...")
	detect(token)

	fmt.Println("\n=== E2E Test Finished ===")
}

func register(username, password string) {
	payload := map[string]string{
		"login":    username,
		"password": password,
	}
	body, _ := json.Marshal(payload)

	resp, err := http.Post(baseURL+"/auth/register", "application/json", bytes.NewBuffer(body))
	if err != nil {
		fmt.Printf("    [X] Request failed: %v\n", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusCreated {
		fmt.Println("    -> Success: User registered (201 Created)")
	} else {
		bodyBytes, _ := io.ReadAll(resp.Body)
		fmt.Printf("    [X] Failed with status %d: %s\n", resp.StatusCode, string(bodyBytes))
	}
}

func login(username, password string) string {
	payload := map[string]string{
		"login":    username,
		"password": password,
	}
	body, _ := json.Marshal(payload)

	resp, err := http.Post(baseURL+"/auth/login", "application/json", bytes.NewBuffer(body))
	if err != nil {
		fmt.Printf("    [X] Request failed: %v\n", err)
		return ""
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		bodyBytes, _ := io.ReadAll(resp.Body)
		fmt.Printf("    [X] Failed with status %d: %s\n", resp.StatusCode, string(bodyBytes))
		return ""
	}

	var result map[string]string
	json.NewDecoder(resp.Body).Decode(&result)
	return result["token"]
}

func history(token string) {
	payload := map[string]any{
		"quantity": 10,
		"flag":     "test",
	}
	body, _ := json.Marshal(payload)

	req, _ := http.NewRequest(http.MethodPost, baseURL+"/history", bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+token)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("    [X] Request failed: %v\n", err)
		return
	}
	defer resp.Body.Close()

	bodyBytes, _ := io.ReadAll(resp.Body)
	if resp.StatusCode == http.StatusOK {
		fmt.Printf("    -> Success: History retrieved: %s\n", string(bodyBytes))
	} else {
		fmt.Printf("    [X] Failed with status %d: %s\n", resp.StatusCode, string(bodyBytes))
	}
}

func detect(token string) {
	filesToUpload := []string{
		"testdata/test1.jpg",
		"testdata/test2.jpg",
	}

	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)

	jsonPayload := `{"targets": ["person", "car", "apple"]}`
	_ = writer.WriteField("payload", jsonPayload)

	filesAttached := 0
	for _, filePath := range filesToUpload {
		file, err := os.Open(filePath)
		if err != nil {
			fmt.Printf("    [!] Warning: Could not open %s (Did you put images in the testdata folder?)\n", filePath)
			continue
		}
		defer file.Close()

		part, err := writer.CreateFormFile("files", filepath.Base(filePath))
		if err != nil {
			fmt.Printf("    [X] Failed to create form file for %s: %v\n", filePath, err)
			continue
		}

		if _, err := io.Copy(part, file); err != nil {
			fmt.Printf("    [X] Failed to copy file content for %s: %v\n", filePath, err)
			continue
		}
		filesAttached++
		fmt.Printf("    -> Attached file: %s\n", filePath)
	}

	if filesAttached == 0 {
		fmt.Println("    [X] Aborting detect request: No files were successfully attached.")
		fmt.Println("    [i] Please place some test images in the 'testdata' directory.")
		return
	}

	writer.Close()

	req, _ := http.NewRequest(http.MethodPost, baseURL+"/detect", body)
	req.Header.Set("Content-Type", writer.FormDataContentType())
	req.Header.Set("Authorization", "Bearer "+token)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("[X] Request failed: %v\n", err)
		return
	}
	defer resp.Body.Close()

	bodyBytes, _ := io.ReadAll(resp.Body)

	if resp.StatusCode == http.StatusInternalServerError {
		fmt.Printf("    -> Received 500 Internal Server Error (Expected if ML service is down).\n")
		fmt.Printf("    -> Response: %s\n", string(bodyBytes))
		fmt.Println("    -> Note: If the error mentions 'ML Service failure', the manager saved the files to volume/ successfully!")
	} else if resp.StatusCode == http.StatusOK {
		fmt.Printf("    -> Success! ML Service responded: %s\n", string(bodyBytes))
	} else {
		fmt.Printf("    [X] Unexpected status %d: %s\n", resp.StatusCode, string(bodyBytes))
	}
}
