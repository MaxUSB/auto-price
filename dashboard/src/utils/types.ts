export interface IResponse {
  success: boolean;
  result: any[];
  error?: string;
}

export type TResponse = IResponse;
