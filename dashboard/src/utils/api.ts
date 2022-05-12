import { TResponse } from './types';
import fetch from 'isomorphic-unfetch';
import queryString from 'query-string';

const api = (
  method: 'get' | 'post',
  endpoint: string,
  params: any = undefined
): Promise<TResponse> => new Promise(resolve => {
  const getQueryString = method === 'get' && params ? `?${queryString.stringify(params)}` : '';
  const body = method !== 'get' && params ? JSON.stringify(params) : undefined;

  fetch(`http://localhost:3001/${endpoint}${getQueryString}`, {
    method: method.toUpperCase(),
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body,
  })
    .then(async response => (
      { status: response.status, result: await response.json() }
    ))
    .then(({ status, result }) => {
      if (status !== 200 || result.success === false) throw new Error(result.error || 'error in api response');
      resolve(result);
    })
    .catch(error => {
      console.error(error);
      resolve({ success: false, data: {}, error });
    });
});

export default api;
