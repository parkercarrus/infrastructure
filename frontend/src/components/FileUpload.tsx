import { Upload, File } from "lucide-react";
import { Card } from "./ui/card";
import { Button } from "./ui/button";
import { useState } from "react";

interface FileUploadProps {
  onFileUpload: (file: File) => void;
  onCodePaste: (code: string) => void;
}

export function FileUpload({ onFileUpload, onCodePaste }: FileUploadProps) {
  const [code, setCode] = useState("");
  const [fileName, setFileName] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setFileName(file.name);
      onFileUpload(file);
    }
  };

  const handleCodeSubmit = () => {
    if (code.trim()) {
      onCodePaste(code);
    }
  };

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <h3 className="mb-4">Upload Model File</h3>
        <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary/50 transition-colors">
          <input
            type="file"
            id="file-upload"
            className="hidden"
            onChange={handleFileChange}
            accept=".py,.js,.ts"
          />
          <label htmlFor="file-upload" className="cursor-pointer">
            <Upload className="mx-auto mb-4 h-12 w-12 text-muted-foreground" />
            <p className="mb-2">
              Drop your model file here or click to browse
            </p>
            <p className="text-muted-foreground">Supports .py, .js, .ts files</p>
          </label>
          {fileName && (
            <div className="mt-4 flex items-center justify-center gap-2 text-primary">
              <File className="h-4 w-4" />
              <span>{fileName}</span>
            </div>
          )}
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="mb-4">Or Paste Code</h3>
        <textarea
          className="w-full min-h-[200px] p-4 bg-input-background rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-ring font-mono"
          placeholder="Paste your model code here..."
          value={code}
          onChange={(e) => setCode(e.target.value)}
        />
        <Button 
          onClick={handleCodeSubmit} 
          className="mt-4 w-full"
          disabled={!code.trim()}
        >
          Run Backtest
        </Button>
      </Card>
    </div>
  );
}
