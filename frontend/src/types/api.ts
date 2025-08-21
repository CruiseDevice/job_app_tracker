export interface ApiResponse<T = any> {
    data: T;
    message?: string;
  }
  
  export interface ApiError {
    detail: string;
  }
  
  export interface WebSocketMessage {
    type: string;
    payload: any;
  }