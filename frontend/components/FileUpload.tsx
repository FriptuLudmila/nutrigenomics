'use client';

import { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle, Shield } from 'lucide-react';

interface FileUploadProps {
  onUpload: (file: File) => void;
  loading: boolean;
}

export default function FileUpload({ onUpload, loading }: FileUploadProps) {
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file: File) => {
    const validExtensions = ['txt', 'csv', 'zip'];
    const fileExtension = file.name.split('.').pop()?.toLowerCase();

    if (fileExtension && validExtensions.includes(fileExtension)) {
      onUpload(file);
    } else {
      alert('Please upload a .txt, .csv, or .zip file from 23andMe or AncestryDNA');
    }
  };

  const onButtonClick = () => {
    inputRef.current?.click();
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-8">
        <h2 className="text-2xl font-semibold text-slate-900 mb-2">
          Upload Genetic Data
        </h2>
        <p className="text-sm text-slate-600">
          Upload your raw DNA file from 23andMe, AncestryDNA, or compatible services
        </p>
      </div>

      <div
        className={`relative border-2 border-dashed rounded-xl p-12 transition-all ${
          dragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-slate-300 bg-white hover:border-slate-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          accept=".txt,.csv,.zip"
          onChange={handleChange}
          disabled={loading}
        />

        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 mb-4">
            <Upload className="w-8 h-8 text-blue-600" />
          </div>

          <h3 className="text-lg font-medium text-slate-900 mb-2">
            Drop your file here, or browse
          </h3>
          <p className="text-sm text-slate-500 mb-6">
            Supports TXT, CSV, ZIP formats
          </p>

          <button
            type="button"
            onClick={onButtonClick}
            disabled={loading}
            className="btn btn-primary"
          >
            {loading ? 'Uploading...' : 'Select File'}
          </button>
        </div>
      </div>

      <div className="mt-8 grid md:grid-cols-3 gap-4">
        <div className="flex items-start gap-3 p-4 bg-white border border-slate-200 rounded-lg">
          <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="text-sm font-medium text-slate-900 mb-1">23andMe</h4>
            <p className="text-xs text-slate-600">Download from account settings</p>
          </div>
        </div>

        <div className="flex items-start gap-3 p-4 bg-white border border-slate-200 rounded-lg">
          <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="text-sm font-medium text-slate-900 mb-1">AncestryDNA</h4>
            <p className="text-xs text-slate-600">Export raw data file</p>
          </div>
        </div>

        <div className="flex items-start gap-3 p-4 bg-white border border-slate-200 rounded-lg">
          <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="text-sm font-medium text-slate-900 mb-1">Other Services</h4>
            <p className="text-xs text-slate-600">Compatible formats accepted</p>
          </div>
        </div>
      </div>

      <div className="mt-6 flex items-start gap-3 p-4 bg-slate-50 border border-slate-200 rounded-lg">
        <Shield className="w-5 h-5 text-slate-700 flex-shrink-0 mt-0.5" />
        <div>
          <h4 className="text-sm font-medium text-slate-900 mb-1">Data Privacy & Security</h4>
          <p className="text-xs text-slate-600">
            Your genetic data is encrypted end-to-end and stored securely. We analyze 25+ variants
            related to nutrition. Data is never shared with third parties.
          </p>
        </div>
      </div>
    </div>
  );
}
