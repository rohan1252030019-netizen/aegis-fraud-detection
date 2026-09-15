"use client";

import React, { useState, useRef } from "react";
import { api, getErrorMessage } from "@/lib/api";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Upload,
  CheckCircle2,
  AlertCircle,
  FileText,
  Download,
  ShieldCheck,
  Zap,
  Layers,
  Sparkles,
  ArrowRight,
  X,
} from "lucide-react";

export default function DataImportPage() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const downloadSampleCsv = () => {
    const csvContent =
      "transaction_id,sender_account_id,receiver_account_id,amount,currency,timestamp\n" +
      "TXN_9001,ACC_1025,ACC_1001,15400.00,USD,2026-09-14T10:15:00Z\n" +
      "TXN_9002,ACC_1025,ACC_1002,14800.00,USD,2026-09-14T10:18:00Z\n" +
      "TXN_9003,ACC_1025,ACC_1003,16200.00,USD,2026-09-14T10:22:00Z\n" +
      "TXN_9004,ACC_1001,ACC_2042,45000.00,USD,2026-09-14T11:00:00Z\n";

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", "aegis_sample_transactions.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    setProgress(20);
    setStatus(null);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      // Simulate progress progression for seamless feedback
      const progressTimer = setInterval(() => {
        setProgress((prev) => (prev < 90 ? prev + 15 : prev));
      }, 300);

      await api.post("/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      clearInterval(progressTimer);
      setProgress(100);
      setStatus(`Successfully processed "${file.name}". Ingestion and multi-layer analysis executed.`);
      setFile(null);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <PageHeader
        title="Data Ingestion & Pipeline"
        description="Upload batch transaction logs (CSV, JSON) to execute multi-layer fraud detection, graph clustering, and behavioral ML profiling."
      />

      {status && (
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-emerald-400 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{status}</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setStatus(null)}
            className="h-7 text-xs text-emerald-400 hover:text-emerald-300"
          >
            Dismiss
          </Button>
        </div>
      )}

      {error && (
        <div className="p-4 bg-destructive/15 border border-destructive/30 rounded-lg text-rose-300 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setError(null)}
            className="h-7 text-xs text-rose-300"
          >
            Dismiss
          </Button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload Form Card (2 cols) */}
        <Card className="lg:col-span-2 border-border/70">
          <CardHeader className="pb-4">
            <CardTitle className="text-sm font-semibold">Upload Batch Transaction File</CardTitle>
            <CardDescription>
              Supported formats: Comma-separated (.csv) or JSON records (.json). Max batch size: 250MB.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleUpload} className="space-y-4">
              {/* Dropzone */}
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200 ${
                  isDragging
                    ? "border-primary bg-primary/5"
                    : file
                    ? "border-emerald-500/40 bg-emerald-500/5"
                    : "border-border/60 hover:border-border hover:bg-muted/20 bg-muted/5"
                }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv,.json"
                  className="hidden"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                />

                <div className="flex flex-col items-center">
                  <div className="h-12 w-12 rounded-full bg-muted/60 flex items-center justify-center text-muted-foreground mb-3">
                    {file ? (
                      <FileText className="w-6 h-6 text-emerald-400" />
                    ) : (
                      <Upload className="w-6 h-6 text-foreground/70" />
                    )}
                  </div>

                  {file ? (
                    <div>
                      <p className="text-sm font-medium text-foreground">{file.name}</p>
                      <p className="text-xs text-muted-foreground font-mono mt-0.5">
                        {(file.size / (1024 * 1024)).toFixed(2)} MB • Ready for Ingestion
                      </p>
                    </div>
                  ) : (
                    <div>
                      <p className="text-xs font-medium text-foreground">
                        Drag and drop your transaction file here, or{" "}
                        <span className="text-primary underline">browse</span>
                      </p>
                      <p className="text-[11px] text-muted-foreground mt-1 font-mono">
                        .CSV or .JSON up to 250MB
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* Upload Progress */}
              {uploading && (
                <div className="space-y-1.5 pt-2">
                  <div className="flex justify-between text-xs font-mono text-muted-foreground">
                    <span>Executing Pipeline...</span>
                    <span>{progress}%</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-1.5 overflow-hidden">
                    <div
                      className="bg-primary h-full transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center gap-3 pt-2">
                <Button
                  type="submit"
                  disabled={!file || uploading}
                  loading={uploading}
                  className="flex-1 h-9 text-xs"
                >
                  {uploading ? "Analyzing Multi-Layer Matrix..." : "Run Detection Pipeline"}
                </Button>
                {file && !uploading && (
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setFile(null)}
                    className="h-9 text-xs"
                  >
                    Clear
                  </Button>
                )}
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Schema Reference & Helper Card (1 col) */}
        <div className="space-y-4">
          <Card className="border-border/70">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Schema Specification
                </CardTitle>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={downloadSampleCsv}
                  className="h-7 text-xs gap-1 text-muted-foreground hover:text-foreground"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Sample CSV</span>
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-2.5 text-xs">
              <p className="text-muted-foreground leading-relaxed text-[11px]">
                Your file must contain the following columns for algorithmic ingestion:
              </p>
              <div className="space-y-1.5 font-mono text-[11px]">
                {[
                  { name: "transaction_id", type: "string", req: "Required" },
                  { name: "sender_account_id", type: "string", req: "Required" },
                  { name: "receiver_account_id", type: "string", req: "Required" },
                  { name: "amount", type: "float", req: "Required" },
                  { name: "currency", type: "string", req: "Optional" },
                  { name: "timestamp", type: "ISO-8601", req: "Required" },
                ].map((col) => (
                  <div
                    key={col.name}
                    className="flex items-center justify-between p-1.5 rounded bg-muted/40 border border-border/40"
                  >
                    <span className="font-semibold text-foreground">{col.name}</span>
                    <span className="text-[10px] text-muted-foreground">{col.type}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Pipeline Verification checklist */}
          <Card className="border-border/70 p-4">
            <h4 className="text-xs font-semibold text-foreground mb-2">Automated Checks Triggered</h4>
            <div className="space-y-2 text-[11px] text-muted-foreground">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span>Zero-loss transaction indexing</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span>Smurfing & structuring detection</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span>Directed acyclic graph update</span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
