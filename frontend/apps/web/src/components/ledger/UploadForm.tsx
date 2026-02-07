import React, { useState } from 'react';
import axios from 'axios';

interface LedgerUploadFormProps {
  onUploadSuccess?: (data: any) => void;
  onUploadError?: (error: any) => void;
}

const LedgerUploadForm: React.FC<LedgerUploadFormProps> = ({ onUploadSuccess, onUploadError }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      const file = event.target.files[0];

      // Validate file type
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/tiff'];
      if (!allowedTypes.includes(file.type)) {
        setError('Invalid file type. Please upload an image file (JPEG, PNG, GIF, BMP, TIFF)');
        setSelectedFile(null);
        return;
      }

      // Validate file size (max 16MB)
      const maxSize = 16 * 1024 * 1024; // 16MB in bytes
      if (file.size > maxSize) {
        setError('File size exceeds 16MB limit');
        setSelectedFile(null);
        return;
      }

      setSelectedFile(file);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file to upload');
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post(`${process.env.NEXT_PUBLIC_BACKEND_API_URL}/api/v1/ledger/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              setUploadProgress(progress);
            }
          },
        }
      );

      if (response.status === 200) {
        onUploadSuccess && onUploadSuccess(response.data);
      } else {
        throw new Error(`Upload failed with status ${response.status}`);
      }
    } catch (err: any) {
      console.error('Upload error:', err);
      setError(err.response?.data?.detail || err.message || 'Upload failed');
      onUploadError && onUploadError(err);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="ledger-upload-form">
      <h3>Upload Daily Ledger</h3>
      <div className="upload-area">
        <label htmlFor="ledger-upload" className="upload-label">
          <div className="upload-instruction">
            <span>Choose an image file or drag and drop it here</span>
            <p>Supported formats: JPEG, PNG, GIF, BMP, TIFF (Max 16MB)</p>
          </div>
        </label>
        <input
          id="ledger-upload"
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="file-input"
        />

        {selectedFile && (
          <div className="file-preview">
            <p>Selected file: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)</p>
            <button onClick={() => setSelectedFile(null)} className="remove-btn">Remove</button>
          </div>
        )}

        {error && <div className="error-message">{error}</div>}

        {isUploading ? (
          <div className="upload-progress">
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <p>Uploading... {uploadProgress}%</p>
          </div>
        ) : (
          <button
            onClick={handleUpload}
            disabled={!selectedFile || isUploading}
            className={`upload-btn ${!selectedFile || isUploading ? 'disabled' : ''}`}
          >
            Upload Ledger
          </button>
        )}
      </div>
    </div>
  );
};

export default LedgerUploadForm;