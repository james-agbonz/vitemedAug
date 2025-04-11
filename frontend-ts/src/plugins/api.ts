import { ComponentTemplate } from "@/class/ComponentTemplate";
import { ax, type AxiosResponse } from "@/plugins/axios-helper";
import emitter from "@/plugins/emitter";

const { post, get } = ax();

interface ComponentAxiosExeConfig<T> {
  success(response: AxiosResponse, target?: T): void;
  error?(error: any, target?: T): void;
  final?(response: AxiosResponse, target?: T): void;
}

class Api<T> {
  componentId: string;
  componentPath: string;
  centralUrl?: string = import.meta.env.VITE_CENTRAL_URL;
  fetchItemListExeConfig?: ComponentAxiosExeConfig<T> | undefined;
  addItemExeConfig?: ComponentAxiosExeConfig<T> | undefined;
  deleteItemExeConfig?: ComponentAxiosExeConfig<T> | undefined;

  constructor(
    componentPath: string,
    fetchItemListExeConfig?: ComponentAxiosExeConfig<T> | undefined,
    addItemExeConfig?: ComponentAxiosExeConfig<T> | undefined,
    deleteItemExeConfig?: ComponentAxiosExeConfig<T> | undefined
  ) {
    this.componentId = componentPath.slice(1);
    const defaultFetchItemListExeConfig: ComponentAxiosExeConfig<T> = {
      success(response, target) {
        if (target && target instanceof ComponentTemplate)
          target.items = response.data;
      },
    };

    const thiz = this;

    const defaultAddItemExeConfig: ComponentAxiosExeConfig<T> = {
      success(response, target) {
        emitter.emit(`${thiz.componentId}-close-add-item-dialog`);
      },
    };

    const defaultDeleteItemExeConfig: ComponentAxiosExeConfig<T> = {
      success(response, target) {
        emitter.emit(`${thiz.componentId}-close-add-item-dialog`);
      },
    };

    this.componentPath = componentPath;
    this.fetchItemListExeConfig = fetchItemListExeConfig
      ? fetchItemListExeConfig
      : defaultFetchItemListExeConfig;
    this.addItemExeConfig = addItemExeConfig
      ? addItemExeConfig
      : defaultAddItemExeConfig;
    this.deleteItemExeConfig = deleteItemExeConfig
      ? deleteItemExeConfig
      : defaultDeleteItemExeConfig;
  }

  fitExeConfig(exeCfg: ComponentAxiosExeConfig<T> | undefined, target?: T) {
    return {
      success: (response: AxiosResponse) =>
        exeCfg?.success ? exeCfg.success(response, target) : undefined,
      error: (error: any) =>
        exeCfg?.error ? exeCfg.error(error, target) : undefined,
      final: (response: AxiosResponse) =>
        exeCfg?.final ? exeCfg.final(response, target) : undefined,
    };
  }

  fetchItemsList(params?: any | undefined, target?: T) {
    console.log("fetch list from", this.componentPath);
    params = params ? params : {};
    this.getRequest(params, this.fetchItemListExeConfig, target);
  }
  addItem(e: SubmitEvent, item: any, target?: T) {
    console.log("add", item);
    post(
      `${this.centralUrl}/task_publisher${this.componentPath}`,
      { act: "create", ...item },
      this.fitExeConfig(this.addItemExeConfig, target)
    );
  }
  deleteItem(item: any, target?: T) {
    console.log("delete", item);
    post(
      `${this.centralUrl}/task_publisher${this.componentPath}`,
      { act: "delete", ...item },
      this.fitExeConfig(this.deleteItemExeConfig, target)
    );
  }

  getRequest(
    params: any,
    exeConfig: ComponentAxiosExeConfig<T> | undefined,
    target?: T
  ) {
    console.log("get from", this.componentPath);
    get(
      `${this.centralUrl}/task_publisher${this.componentPath}`,
      params,
      this.fitExeConfig(exeConfig, target)
    );
  }

  postRequest(
    params: any,
    exeConfig: ComponentAxiosExeConfig<T> | undefined,
    target?: T
  ) {
    console.log("post to", this.componentPath);
    console.log("with", params);
    post(
      `${this.centralUrl}/task_publisher${this.componentPath}`,
      params,
      this.fitExeConfig(exeConfig, target)
    );
  }
}

export default Api;
export type { ComponentAxiosExeConfig };
