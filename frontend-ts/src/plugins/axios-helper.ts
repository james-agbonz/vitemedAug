import axios, {
  AxiosHeaders,
  type AxiosRequestConfig,
  type AxiosResponse,
} from "axios";

export interface AxiosExeConfig {
  success(response: AxiosResponse): void;
  error?(error: any): void;
  final?(response: AxiosResponse): void;
}

export function ax() {
  function universalErrorHandler(
    axiosReqConfig: AxiosRequestConfig,
    error: any
  ) {
    console.error(axiosReqConfig);
    console.error(error);
  }

  function execute(axiosReqConfig: AxiosRequestConfig, config: AxiosExeConfig) {
    let currentResponse: AxiosResponse<any, any>;
    axios(axiosReqConfig)
      .then(function (response) {
        if (
          config.success !== undefined &&
          typeof config.success === "function"
        ) {
          config.success(response);
          currentResponse = response;
        }
      })
      .catch(function (error) {
        universalErrorHandler(axiosReqConfig, error);
        if (config.error !== undefined && typeof config.error === "function") {
          config.error(error);
        } else {
          console.log(error);
        }
      })
      .then(function () {
        if (config.final !== undefined && typeof config.final === "function") {
          config.final(currentResponse);
        }
      });
  }

  function post(url: string, dataObj: any, config: AxiosExeConfig) {
    // isAuth, success, error, final
    let headers = new AxiosHeaders();
    headers.setContentType("multipart/form-data");
    const formData = new FormData();

    for (let key of Object.keys(dataObj)) {
      formData.append(key, dataObj[key]);
    }

    var axiosReqConfig: AxiosRequestConfig = {
      method: "post",
      url,
      headers,
      data: formData,
    };
    execute(axiosReqConfig, config);
  }

  function get(url: string, params: any, config: AxiosExeConfig) {
    let headers = new AxiosHeaders();
    var axiosReqConfig = {
      method: "get",
      url,
      headers,
      params,
    };
    execute(axiosReqConfig, config);
  }
  return { post, get };
}
export type { AxiosResponse };
