import axios, { AxiosResponse, InternalAxiosRequestConfig } from "axios";
import {
  MOCK_OVERVIEW_METRICS,
  MOCK_ALERTS,
  MOCK_ACCOUNTS,
  MOCK_TRANSACTIONS,
  MOCK_CASES,
  MOCK_GRAPH_SUBGRAPH,
  MOCK_INVESTIGATION_RESULT,
  MOCK_VALIDATION_RESULT,
  MOCK_UPLOAD_RESULT,
} from "./mockData";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  headers: { "Content-Type": "application/json" },
  timeout: 5000,
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("aegis_token");
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Mock state machine for interactive demo simulations (e.g. running investigations)
let mockJobStartTime = 0;
let mockJobState: any = null;

function getMockResponse(url: string, method: string): any {
  const cleanUrl = url.toLowerCase();

  if (cleanUrl.includes("/analytics/overview")) {
    return MOCK_OVERVIEW_METRICS;
  }

  if (cleanUrl.includes("/alerts")) {
    return {
      items: MOCK_ALERTS,
      total: MOCK_ALERTS.length,
      page: 1,
      page_size: MOCK_ALERTS.length,
    };
  }

  if (cleanUrl.includes("/accounts")) {
    const match = cleanUrl.match(/\/accounts\/([a-z0-9_-]+)/);
    if (match && match[1] && !["search", "filter"].includes(match[1])) {
      const accId = match[1].toUpperCase();
      const found = MOCK_ACCOUNTS.find((a) => a.account_id.toUpperCase() === accId);
      return found || MOCK_ACCOUNTS[0];
    }
    return {
      items: MOCK_ACCOUNTS,
      total: MOCK_ACCOUNTS.length,
      page: 1,
      page_size: MOCK_ACCOUNTS.length,
    };
  }

  if (cleanUrl.includes("/transactions")) {
    return {
      items: MOCK_TRANSACTIONS,
      total: MOCK_TRANSACTIONS.length,
      page: 1,
      page_size: MOCK_TRANSACTIONS.length,
    };
  }

  if (cleanUrl.includes("/graph")) {
    return MOCK_GRAPH_SUBGRAPH;
  }

  if (cleanUrl.includes("/cases")) {
    if (method === "post" && cleanUrl.includes("/investigate/")) {
      const parts = url.split("/");
      const accountId = parts[parts.length - 1] || "ACC00048599";
      const caseId = parts[parts.indexOf("cases") + 1] || "CAS-2026-001";
      mockJobStartTime = Date.now();
      mockJobState = {
        job_id: `JOB-${Date.now()}`,
        case_id: caseId,
        account_id: accountId,
        status: "RUNNING",
        current_stage: "TRANSFORMER_INFERENCE",
        current_stage_label: "Transformer Sequence Inference",
        started_at: new Date().toISOString(),
        completed_at: null,
        elapsed_ms: 120,
        stages: MOCK_INVESTIGATION_RESULT.pipeline_trace.map((s, idx) => ({
          ...s,
          status: idx < 3 ? "COMPLETED" : idx === 3 ? "RUNNING" : "PENDING",
        })),
        error: null,
        failed_stage: null,
        result: null,
      };
      return mockJobState;
    }

    if (cleanUrl.includes("/cancel")) {
      if (mockJobState) {
        mockJobState.status = "CANCELLED";
      }
      return { status: "CANCELLED" };
    }

    if (cleanUrl.includes("/investigations/")) {
      const elapsed = Date.now() - mockJobStartTime;
      if (mockJobState) {
        if (elapsed > 1800) {
          mockJobState.status = "COMPLETED";
          mockJobState.completed_at = new Date().toISOString();
          mockJobState.stages = MOCK_INVESTIGATION_RESULT.pipeline_trace;
          mockJobState.result = MOCK_INVESTIGATION_RESULT;
        } else {
          const totalStages = MOCK_INVESTIGATION_RESULT.pipeline_trace.length;
          const stageIndex = Math.min(
            totalStages - 1,
            Math.floor((elapsed / 1800) * totalStages)
          );
          mockJobState.stages = MOCK_INVESTIGATION_RESULT.pipeline_trace.map((s, idx) => ({
            ...s,
            status: idx < stageIndex ? "COMPLETED" : idx === stageIndex ? "RUNNING" : "PENDING",
          }));
        }
        return mockJobState;
      }
      return {
        status: "COMPLETED",
        completed_at: new Date().toISOString(),
        stages: MOCK_INVESTIGATION_RESULT.pipeline_trace,
        result: MOCK_INVESTIGATION_RESULT,
      };
    }

    if (cleanUrl.includes("/feedback")) {
      return { status: "SUCCESS", message: "Compliance decision logged" };
    }

    return {
      items: MOCK_CASES,
      total: MOCK_CASES.length,
      page: 1,
      page_size: MOCK_CASES.length,
    };
  }

  if (cleanUrl.includes("/upload/validate")) {
    return MOCK_VALIDATION_RESULT;
  }

  if (cleanUrl.includes("/upload/sample")) {
    return (
      "transaction_id,sender_account_id,receiver_account_id,amount,currency,timestamp,transaction_type,beneficiary_id,merchant_id,device_id,ip_address,location,channel,account_balance\n" +
      "TX_SMP_1001,ACC_1025,ACC_1001,48500.00,INR,2026-09-14T09:15:22Z,TRANSFER,BEN_901,MERCH_01,DEV_ANDROID_991,192.168.1.45,Mumbai,MOBILE_BANKING,150000.00\n" +
      "TX_SMP_1002,ACC_1025,ACC_1002,49200.00,INR,2026-09-14T09:18:45Z,TRANSFER,BEN_902,MERCH_01,DEV_ANDROID_991,192.168.1.45,Mumbai,MOBILE_BANKING,101500.00\n" +
      "TX_SMP_1003,ACC_1025,ACC_1003,49800.00,INR,2026-09-14T09:22:10Z,TRANSFER,BEN_903,MERCH_01,DEV_ANDROID_991,192.168.1.45,Mumbai,MOBILE_BANKING,52300.00\n" +
      "TX_SMP_1004,ACC_1001,ACC_1035,48000.00,INR,2026-09-14T10:05:00Z,TRANSFER,BEN_904,MERCH_02,DEV_IOS_332,192.168.1.78,Pune,ONLINE_NETBANKING,48500.00\n"
    );
  }

  if (cleanUrl.includes("/upload")) {
    return MOCK_UPLOAD_RESULT;
  }

  return null;
}

// Global response interceptor: intercepts Network Errors, Mixed Content blocks, 
// and connection failures when live backend is offline or unconfigured on Vercel
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: any) => {
    const isNetworkError =
      !error.response ||
      error.message === "Network Error" ||
      error.code === "ERR_NETWORK" ||
      error.code === "ECONNABORTED" ||
      error.code === "ECONNREFUSED" ||
      error.response?.status === 404 ||
      error.response?.status >= 500;

    if (isNetworkError) {
      const url = error.config?.url || "";
      const method = (error.config?.method || "get").toLowerCase();
      const mockData = getMockResponse(url, method);

      if (mockData !== null && mockData !== undefined) {
        console.warn(
          `[AEGIS Engine] Live backend unreachable at ${url}. Seamlessly serving simulated compliance telemetry.`
        );
        return Promise.resolve({
          data: mockData,
          status: 200,
          statusText: "OK (Simulated Offline Mode)",
          headers: {},
          config: error.config,
        });
      }
    }

    return Promise.reject(error);
  }
);

export function getErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    return err.response?.data?.detail || err.message || "An unexpected error occurred";
  }
  return String(err);
}
