export interface IResponse {
  success: boolean;
  data: any;
  error?: string;
}

export type TResponse = IResponse;

export interface IDictionary<T> {
  [key: string]: T;
}
