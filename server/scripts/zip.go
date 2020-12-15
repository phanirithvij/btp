package main

import (
	"archive/zip"
	"bytes"
	jsonp "encoding/json"
	"errors"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"path/filepath"

	"github.com/schollz/progressbar"
)

// ZipArgs ...
type ZipArgs struct {
	UpdateURL string `json:"update_url"`
	UserID    string `json:"user_id"`
	Status    string `json:"status"`
	TaskID    string `json:"taskid"`
}

// ZipFiles compresses one or many files into a single zip archive file.
// Param 1: filename is the output zip file's name.
// Param 2: files is a list of files to add to the zip.
func ZipFiles(filename string, folder string) error {

	newZipFile, err := os.Create(filename)
	if err != nil {
		return err
	}
	defer newZipFile.Close()

	zipWriter := zip.NewWriter(newZipFile)
	defer zipWriter.Close()

	currDir, err := os.Getwd()

	log.Println(currDir, filepath.Base(folder))

	// Add files to zip
	if info, _ := os.Stat(folder); info.IsDir() {
		localFiles := []string{}
		err = filepath.Walk(folder, func(path string, info os.FileInfo, err error) error {
			// if a file
			if fileinfo, err := os.Stat(path); fileinfo.Mode().IsRegular() && err == nil {
				localFiles = append(localFiles, path)
				// log.Println("Added", path)
			}
			return nil
		})

		count := int64(len(localFiles))
		bar := progressbar.Default(count)

		log.Println("Number of files", count)

		// Important
		// or it will become highly nested
		upOne, err := filepath.Abs(filepath.Join(folder, ".."))
		os.Chdir(upOne)
		if err != nil {
			panic(err)
		}
		for _, loc := range localFiles {
			bar.Add(1)
			// log.Println("DAMNIT")
			relpath, err := filepath.Rel(upOne, loc)
			// log.Println(relpath)
			if err != nil {
				panic(err)
			}
			if err = addFileToZip(zipWriter, filepath.Join(relpath)); err != nil {
				return err
			}
		}
		os.Chdir(currDir)
		return nil
	}
	return errors.New("not a directory")
}

// addFileToZip Adds a file to the zip
func addFileToZip(zipWriter *zip.Writer, filename string) error {

	// log.Println(filename)

	fileToZip, err := os.Open(filename)
	if err != nil {
		return err
	}
	defer fileToZip.Close()

	// Get the file information
	info, err := fileToZip.Stat()
	if err != nil {
		return err
	}

	header, err := zip.FileInfoHeader(info)
	if err != nil {
		return err
	}

	// Using FileInfoHeader() above only uses the basename of the file. If we want
	// to preserve the folder structure we can overwrite this with the full path.
	header.Name = filename

	// Change to deflate to gain better compression
	// see http://golang.org/pkg/archive/zip/#pkg-constants
	header.Method = zip.Deflate

	writer, err := zipWriter.CreateHeader(header)
	if err != nil {
		return err
	}
	_, err = io.Copy(writer, fileToZip)
	return err
}

// Usage go run zip.go dirname zippath
// eg: go run zip.go . currfolder.zip
func main() {
	// Do not use this as a service
	// Because it will become something like celery

	log.Println(os.Args)
	if len(os.Args) < 4 {
		panic("Wrong usage pass dir, name, progress_url")
	}
	path, err := filepath.Abs(os.Args[1])
	if err != nil {
		panic(err)
	}
	url := "http://localhost:3000/progress"
	data := &ZipArgs{Status: "Ok", TaskID: "jdiewuc", UpdateURL: "/", UserID: "aja"}

	sendReq(data, url)

	err = ZipFiles(
		filepath.Join(os.Args[2]),
		path)
	if err != nil {
		panic(err)
	}
}

func sendReq(data *ZipArgs, url string) error {
	jsonBytes, err := jsonp.Marshal(data)
	if err != nil {
		return err
	}
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonBytes))
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return err

	}
	defer resp.Body.Close()
	return nil
}

// LoadFromJSON ...
func LoadFromJSON(src string) (*ZipArgs, error) {

	d := new(ZipArgs)
	data, err := ioutil.ReadFile(src)
	if err != nil {
		return d, err
	}

	err = jsonp.Unmarshal(data, &d)
	if err != nil {
		return d, err
	}
	return d, err
}
