import {TResponse} from "./types";
import fetch from 'isomorphic-unfetch';
import queryString from "query-string";

const api = (
  method: 'get' | 'post',
  module: string,
  params: any = undefined
): Promise<TResponse> => new Promise(resolve => {
  const getQueryString = method === 'get' && params ? `?${queryString.stringify(params)}` : '';
  const body = method !== 'get' && params ? JSON.stringify(params) : undefined;

  fetch(`http://localhost:3001/${module}${getQueryString}`, {
    method: method.toUpperCase(),
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body,
  })
    .then(async response => (
      {status: response.status, data: await response.json()}
    ))
    .then(({status, data}) => {
      if (status !== 200 || data.success === false) throw new Error(data.error || 'error in api response');
      resolve(data);
    })
    .catch(error => {
      console.error(error);
      resolve({success: false, result: [], error});
    });
});

export default api;
