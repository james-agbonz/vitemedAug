import type Api from "@/plugins/api";

interface ComponentConfig {
  column: string;
  width: number;
  key: string;
  render?(value: string, index: any): string;
  center?: boolean;
}

class ComponentTemplate {
  api: Api<ComponentTemplate>;

  configs: ComponentConfig[];
  columnValueRenderMap: Map<string, Function | undefined>;
  currentItem?: any;

  items?: any[];
  itemKeyList: string[];
  itemStatus?: string[];

  executionConfigs?: ComponentConfig[];
  currentExecutions?: any[];
  currentExecution: any;
  currentExecutionResultList?: any[];
  executionKeyList?: string[];

  initCurrent: () => void;

  constructor(
    configs: ComponentConfig[],
    api: Api<ComponentTemplate>,
    initCurrent: () => void
  ) {
    this.configs = configs;
    this.api = api;

    this.itemKeyList = [];
    this.items = [];

    this.columnValueRenderMap = new Map();
    configs.forEach((conf) => {
      this.itemKeyList.push(conf.key);
      this.columnValueRenderMap.set(conf.key, conf.render);
    });

    this.initCurrent = initCurrent;
    this.clear();
  }

  clear() {
    this.currentExecutions = [];
    this.currentItem = this.initCurrent();
    this.currentExecutionResultList = [];
    this.currentExecution = undefined;
  }

  checkItemListHasRunning() {
    for (const item of this.items!) {
      if (item.task_status === "running") {
        return true;
      }
    }
    return false;
  }

  fetchItemsList() {
    this.api.fetchItemsList(undefined, this);
  }
  addItem(e: SubmitEvent) {
    this.api.addItem(e, this.currentItem, this);
  }
  deleteItem(item: any) {
    this.api.deleteItem(item, this);
  }
}

export { ComponentTemplate };
