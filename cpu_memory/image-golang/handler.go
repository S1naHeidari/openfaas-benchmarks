package function

import (
	"encoding/json"
	"fmt"
	"image"
	"image/jpeg"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"time"

	"github.com/disintegration/imaging"
)

func Handle(w http.ResponseWriter, r *http.Request) {
	request := make(map[string]string)
	err := json.NewDecoder(r.Body).Decode(&request)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	inputBucket := request["input_bucket"]
	objectKey := request["object_key"]
	outputBucket := request["output_bucket"]
	keyID := request["key_id"]
	accessKey := request["access_key"]
	requestUUID := request["uuid"]
	startTime := time.Now()

	downloadPath := "/tmp/pics/" + uuid.New().String() + ".jpg"
	resp, err := http.Get("https://sample-videos.com/img/Sample-jpg-image-1mb.jpg")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		http.Error(w, fmt.Sprintf("unexpected status code: %d", resp.StatusCode), http.StatusInternalServerError)
		return
	}

	file, err := os.Create(downloadPath)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer file.Close()

	_, err = io.Copy(file, resp.Body)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	pathList, err := imageProcessing(objectKey, downloadPath)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	for _, uploadPath := range pathList {
		err := uploadFile(uploadPath, outputBucket, filepath.Base(uploadPath), keyID, accessKey)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
	}

	latency := time.Since(startTime)
	response := map[string]interface{}{
		"statusCode": 200,
		"body": map[string]interface{}{
			"latency":    latency.Seconds(),
			"start_time": startTime,
			"uuid":       requestUUID,
			"test_name":  "image-processing",
		},
	}

	jsonResponse, err := json.Marshal(response)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	w.Write(jsonResponse)
}

func imageProcessing(objectKey, imagePath string) ([]string, error) {
	var pathList []string

	image, err := imaging.Open(imagePath)
	if err != nil {
		return nil, err
	}

	tmp := image
	pathList = append(pathList, resize(image, objectKey))

	return pathList, nil
}

func resize(image *image.NRGBA, file_name string) string {
	name := filepath.Base(file_name)
	path := "/tmp/pics/resized-" + uuid.New().String() + name

	dstImage := imaging.Resize(image, 128, 128, imaging.Lanczos)
	err := imaging.Save(dstImage, path)
	if err != nil {
		log.Printf("failed to save image: %v", err)
	}

	return path
}

func uploadFile(filePath, bucket, objectKey, keyID, accessKey string) error {
	file, err := os.Open(filePath)
	if err != nil {
		return err
	}
	defer file.Close()

	cfg := &aws.Config{
		Credentials: credentials.NewStaticCredentials(keyID, accessKey, ""),
		Region:      aws.String("us-east-1"), // Change region as needed
		Endpoint:    aws.String("http://192.168.56.10:32390"),
		S3ForcePathStyle: aws.Bool(true),
	}

	sess := session.Must(session.NewSession(cfg))

	uploader := s3manager.NewUploader(sess)
	_, err = uploader.Upload(&s3manager.UploadInput{
		Bucket: aws.String(bucket),
		Key:    aws.String(objectKey),
		Body:   file,
	})
	if err != nil {
		return err
	}

	return nil
}

