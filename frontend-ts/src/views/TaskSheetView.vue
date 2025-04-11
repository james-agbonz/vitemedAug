<template>
  <ComponentMgmt
    :ref="`${id}_component`"
    :component-id="id"
    title="Task Sheet"
    add-btn-text="Add"
    :component="component"
    :item-viewable="true"
    :has-executions="true"
    :before-open-add-item-dialog-hook="beforeOpenAddItemDialogHook"
    :before-open-view-item-dialog-hook="beforeOpenViewItemDialogHook"
    :execution-result-dialog-active-hook="executionResultDialogActiveHook"
    :before-add-item-hook="beforeAddItemHook"
    :get-item-execution-list="getItemExecutionList"
    :init-item="initItem"
    :execution-with-item-ticket="executionWithItemTicket"
    :execution-with-item-directly="executionWithItemDirectly"
    :stop-a-execution="stopAExecution"
    :delete-a-execution="deleteAExecution"
    :get-item-execution-result="getItemExecutionResult"
    :status-on-list="true"
  >
    <template #itemAddForm>
      <v-row>
        <v-select
          label="Task Type*"
          :items="task_type_options"
          item-title="label"
          item-value="value"
          v-model="component.currentItem.task_type"
          name="task_type"
          required
          density="compact"
          autocomplete="off"
        ></v-select>
      </v-row>
      <v-row>
        <v-text-field
          label="Task Sheet Name*"
          name="name"
          v-model="component.currentItem.task_sheet_name"
          required
          density="compact"
          autocomplete="off"
        ></v-text-field>
      </v-row>
      <v-row>
        <v-select
          label="DB Service*"
          :items="db_service_list"
          item-title="label"
          item-value="value"
          name="db_service_executor_id"
          v-model="component.currentItem.db_service_executor_id"
          required
          density="compact"
          autocomplete="off"
        ></v-select>
      </v-row>
      <v-row>
        <v-select
          label="Model Service*"
          :items="model_service_list"
          item-title="label"
          item-value="value"
          name="model_service_executor_id"
          v-model="component.currentItem.model_service_executor_id"
          required
          density="compact"
          autocomplete="off"
        ></v-select>
      </v-row>
      <v-row v-if="component.currentItem.task_type?.includes('xai')">
        <v-select
          label="XAI Service*"
          :items="xai_service_list"
          item-title="label"
          item-value="value"
          name="xai_service_executor_id"
          v-model="component.currentItem.xai_service_executor_id"
          required
          density="compact"
          autocomplete="off"
        ></v-select>
      </v-row>
      <v-row v-if="component.currentItem.task_type === 'xai_evaluation'">
        <v-col cols="4">
          <v-switch
            density="compact"
            label="Use Exist"
            color="warning"
            :disabled="
              component.currentItem.xai_service_executor_id === undefined
            "
            v-model="use_exist_xai_execution"
            :hide-details="
              (use_exist_xai_execution &&
                exist_model_xai_execution_list.length > 0) ||
              component.currentItem.previous_task_ticket
            "
          ></v-switch>
        </v-col>
        <v-col cols="8">
          <v-select
            label="Use Previous XAI Executions"
            :items="exist_model_xai_execution_list"
            item-title="task_execution_name"
            item-value="task_ticket"
            name="previous_task_ticket"
            :disabled="!use_exist_xai_execution"
            v-model="component.currentItem.previous_task_ticket"
            density="compact"
            autocomplete="off"
          ></v-select>
        </v-col>
      </v-row>
      <v-row v-if="component.currentItem.task_type === 'model_evaluation'">
        <v-select
          label="Model Evaluation Service*"
          :items="model_evaluation_service_list"
          item-title="label"
          item-value="value"
          name="model_evaluation_service_executor_id"
          v-model="component.currentItem.model_evaluation_service_executor_id"
          required
          density="compact"
          autocomplete="off"
        ></v-select>
      </v-row>
      <v-row v-if="component.currentItem.task_type === 'xai_evaluation'">
        <v-select
          label="XAI Evaluation Service*"
          :items="xai_evaluation_service_list"
          item-title="label"
          item-value="value"
          name="xai_evaluation_service_executor_id"
          v-model="component.currentItem.xai_evaluation_service_executor_id"
          required
          density="compact"
          autocomplete="off"
        ></v-select>
      </v-row>
      <v-row
        v-if="
          ['xai', 'model_evaluation'].includes(component.currentItem.task_type)
        "
      >
        <v-col cols="4">
          <v-switch
            density="compact"
            label="Use Exist"
            color="warning"
            :disabled="
              component.currentItem.model_service_executor_id === undefined
            "
            v-model="use_exist_training_execution"
            :hide-details="
              (use_exist_training_execution &&
                exist_model_training_execution_list.length > 0) ||
              component.currentItem.previous_task_ticket
            "
          ></v-switch>
        </v-col>
        <v-col cols="8">
          <v-select
            label="Use Previous Model Train Executions"
            :items="exist_model_training_execution_list"
            item-title="task_execution_name"
            item-value="task_ticket"
            name="previous_task_ticket"
            :disabled="!use_exist_training_execution"
            v-model="component.currentItem.previous_task_ticket"
            density="compact"
            autocomplete="off"
          ></v-select>
        </v-col>
      </v-row>
      <v-row>
        <v-select
          label="Dataset Configuration"
          :items="dataset_configuration_list"
          item-title="configuration_name"
          item-value="configuration_id"
          name="dataset_configuration_id"
          v-model="component.currentItem.dataset_configuration_id"
          multiple
          density="compact"
          autocomplete="off"
        ></v-select>
      </v-row>
      <v-row v-if="!component.currentItem.task_type.includes('xai')">
        <v-select
          label="Model Configuration"
          :items="model_configuration_list"
          item-title="configuration_name"
          item-value="configuration_id"
          name="model_configuration_id"
          v-model="component.currentItem.model_configuration_id"
          density="compact"
          autocomplete="off"
        ></v-select>
      </v-row>
      <v-row v-if="!component.currentItem.task_type.includes('xai')">
        <v-select
          label="Trainer Configuration"
          :items="trainer_configuration_list"
          item-title="configuration_name"
          item-value="configuration_id"
          name="trainer_configuration_id"
          v-model="component.currentItem.trainer_configuration_id"
          required
          density="compact"
          autocomplete="off"
        ></v-select>
      </v-row>
      <v-row>
        <v-select
          label="Task Function Key*"
          :items="available_task_function_keys"
          name="task_function_key"
          v-model="component.currentItem.task_function_key"
          required
          density="compact"
          autocomplete="off"
        ></v-select>
      </v-row>
      <v-row>
        <v-textarea
          label="Task Parameters"
          name="task_parameters"
          v-model="component.currentItem.task_parameters"
          density="compact"
        ></v-textarea>
      </v-row>
    </template>

    <template #itemForExecutions="{ item }">
      <td>{{ item.task_execution_name }}</td>
      <td>{{ item.task_ticket }}</td>
      <td>{{ timestampFormat(item.start_time) }}</td>
      <td>{{ timestampFormat(item.end_time) }}</td>
      <ExecutionStatus :task_status="item.task_status" />
    </template>
  </ComponentMgmt>
</template>

<script lang="ts" setup>
import ComponentMgmt from "@/components/ComponentMgmt.vue";
import { ComponentTemplate } from "@/class/ComponentTemplate";
import { onUnmounted, ref, watch } from "vue";
import {
  capitalizeFirstLetter,
  getStateUpdateMap,
  timestampFormat,
} from "@/plugins/global";
import type { ComponentAxiosExeConfig } from "@/plugins/api";
import emitter from "@/plugins/emitter";
import Api from "@/plugins/api";
import ExecutionStatus from "@/components/ExecutionStatus.vue";

const id = "task_sheet";
const task_type_options: any[] = [
  { label: "Training", value: "training" },
  { label: "Model Evaluation", value: "model_evaluation" },
  { label: "XAI", value: "xai" },
  { label: "XAI Evaluation", value: "xai_evaluation" },
];

const task_sheet_component = ref(null);

const db_service_list = ref<any>([]);
const xai_service_list = ref<any>([]);
const model_service_list = ref<any>([]);
const xai_evaluation_service_list = ref<any>([]);
const model_evaluation_service_list = ref<any>([]);

const dataset_configuration_list = ref<any>([]);
const model_configuration_list = ref<any>([]);
const trainer_configuration_list = ref<any>([]);

const available_task_function_keys = ref<any>([]);

const use_exist_training_execution = ref<boolean>(false);
const use_exist_xai_execution = ref<boolean>(false);
const exist_model_training_execution_list = ref<any>([]);
const exist_model_xai_execution_list = ref<any>([]);

const stateUpdateMap = getStateUpdateMap();

stateUpdateMap.set("TASK_STATUS_UPDATE", (data: any) => {
  if (component.value.currentExecutions) {
    for (const itemExe of component.value.currentExecutions) {
      if (itemExe.task_ticket === data.task_ticket) {
        itemExe.task_status = data.current_task_execution.task_status;
        break;
      }
    }
  }
  if (!task_sheet_component.value?.["executionDialogActive"]) {
    component.value.fetchItemsList();
  }
});

const taskSheetApi = new Api<ComponentTemplate>("/task_sheet");

let component = ref<ComponentTemplate>(
  new ComponentTemplate(
    [
      {
        column: "#",
        width: 4,
        key: "configuration_id",
        center: true,
        render(v, i) {
          return i + 1;
        },
      },
      // {
      //   column: "ID",
      //   width: 10,
      //   key: "task_sheet_id",
      // },
      {
        column: "Name",
        width: 18,
        key: "task_sheet_name",
      },
      {
        column: "Task Type",
        width: 15,
        key: "task_type",
        render: (v) => {
          return capitalizeFirstLetter(v);
        },
      },
    ],
    taskSheetApi,
    () => {
      return {
        task_type: "training",
        task_parameters: "{}",
      };
    }
  )
);

component.value.executionConfigs = [
  {
    column: "Task Name",
    width: 12,
    key: "task_name",
  },
  {
    column: "Task Ticket",
    width: 12,
    key: "task_ticket",
  },
  {
    column: "Start Time",
    width: 15,
    key: "start_time",
  },
  {
    column: "End Time",
    width: 15,
    key: "end_time",
  },
  {
    column: "Status",
    width: 5,
    key: "task_name",
    center: true,
  },
];

const executorTaskFuncKeyApi = new Api<any>("/executor_task_function_key");

function getTaskExecutorFunctionKey() {
  available_task_function_keys.value = [];
  let executor_id;
  switch (component.value.currentItem.task_type) {
    case "xai":
      executor_id = component.value.currentItem.xai_service_executor_id;
      break;
    case "training":
      executor_id = component.value.currentItem.model_service_executor_id;
      break;
    case "xai_evaluation":
      executor_id =
        component.value.currentItem.xai_evaluation_service_executor_id;
      break;
    case "model_evaluation":
      executor_id =
        component.value.currentItem.model_evaluation_service_executor_id;
      break;
    default:
      executor_id = undefined;
      break;
  }
  console.log(
    "getTaskExecutorFunctionKey",
    component.value.currentItem.task_type,
    executor_id
  );
  if (executor_id) {
    executorTaskFuncKeyApi.getRequest(
      {
        executor_id,
      },
      {
        success(response, target) {
          available_task_function_keys.value = response.data;
          component.value.currentItem.task_function_key =
            available_task_function_keys.value[0];
        },
      }
    );
  }
}

watch(
  () => [
    component.value.currentItem.task_type,
    component.value.currentItem.xai_service_executor_id,
    component.value.currentItem.model_service_executor_id,
    component.value.currentItem.xai_evaluation_service_executor_id,
    component.value.currentItem.model_evaluation_service_executor_id,
  ],
  (nv, ov) => {
    // https://blog.csdn.net/yyzx_yyzx/article/details/126301837
    // console.log(
    //   task_sheet_component.value?.["addItemDialogActive"],
    //   task_sheet_component.value?.["executionDialogActive"]
    // );
    if (task_sheet_component.value?.["addItemDialogActive"])
      getTaskExecutorFunctionKey();
  },
  { deep: true, immediate: true }
);

watch(
  () => task_sheet_component.value?.["executionDialogActive"],
  (open, ov) => {
    component.value.fetchItemsList();
  }
);

watch(
  () => use_exist_training_execution.value,
  (n, o) => {
    if (n && component.value.currentItem.model_service_executor_id) {
      taskExecutionApi.getRequest(
        {
          task_type: "training",
          executor_id: component.value.currentItem.model_service_executor_id,
        },
        {
          success(response, target) {
            exist_model_training_execution_list.value = response.data;
          },
        }
      );
    } else {
      component.value.currentItem.previous_task_ticket = undefined;
    }
  }
);

watch(
  () => use_exist_xai_execution.value,
  (n, o) => {
    if (n && component.value.currentItem.model_service_executor_id) {
      taskExecutionApi.getRequest(
        {
          task_type: "xai",
          executor_id: component.value.currentItem.xai_service_executor_id,
        },
        {
          success(response, target) {
            exist_model_xai_execution_list.value = response.data;
          },
        }
      );
    } else {
      component.value.currentItem.previous_task_ticket = undefined;
    }
  }
);

const executorApi = new Api<any>("/executor");
const configurationApi = new Api<any>("/configuration");

function beforeOpenAddItemDialogHook() {
  db_service_list.value = [];
  xai_service_list.value = [];
  model_service_list.value = [];
  xai_evaluation_service_list.value = [];
  model_evaluation_service_list.value = [];
  available_task_function_keys.value = [];

  use_exist_training_execution.value = false;
  exist_model_training_execution_list.value = [];
  use_exist_xai_execution.value = false;
  exist_model_xai_execution_list.value = [];

  executorApi.fetchItemListExeConfig = {
    success(response, _) {
      for (const item of response.data) {
        const displayI = {
          label: item.executor_name,
          value: item.executor_id,
        };

        if (item.executor_type === "dataset") {
          db_service_list.value.push(displayI);
          // component.value.currentItem.db_service_executor_id = displayI.value;
        }
        if (item.executor_type === "xai") {
          xai_service_list.value.push(displayI);
          // component.value.currentItem.xai_service_executor_id = displayI.value;
        }
        if (item.executor_type === "model") {
          model_service_list.value.push(displayI);
          // component.value.currentItem.model_service_executor_id =
          //   displayI.value;
        }
        if (item.executor_type === "xai_evaluation") {
          xai_evaluation_service_list.value.push(displayI);
          // component.value.currentItem.xai_evaluation_service_executor_id =
          //   displayI.value;
        }
        if (item.executor_type === "model_evaluation") {
          model_evaluation_service_list.value.push(displayI);
          // component.value.currentItem.model_evaluation_service_executor_id =
          //   displayI.value;
        }
      }
    },
  };
  executorApi.fetchItemsList();

  dataset_configuration_list.value = [];
  model_configuration_list.value = [];
  trainer_configuration_list.value = [];

  configurationApi.fetchItemListExeConfig = {
    success(response, _) {
      response.data.forEach((configuration: any) => {
        if (configuration.configuration_type === "dataset") {
          dataset_configuration_list.value.push(configuration);
          // component.value.currentItem.dataset_configuration_id =
          //   configuration.configuration_id;
        }
        if (configuration.configuration_type === "model") {
          model_configuration_list.value.push(configuration);
          // component.value.currentItem.model_configuration_id =
          //   configuration.configuration_id;
        }
        if (configuration.configuration_type === "trainer") {
          trainer_configuration_list.value.push(configuration);
          // component.value.currentItem.trainer_configuration_id =
          //   configuration.configuration_id;
        }
      });
    },
  };
  configurationApi.fetchItemsList();
}

function beforeOpenViewItemDialogHook(item: any) {
  beforeOpenAddItemDialogHook();
  for (const paramKey of Object.keys(item.task_parameters)) {
    item[paramKey] = item.task_parameters[paramKey];
  }
  item.task_parameters = JSON.stringify(item.task_parameters);
}

function executionResultDialogActiveHook(ifOpen: boolean) {
  if (!ifOpen) {
    taskExecutionResultApi.getRequest(
      {
        act: "stop_ws_stream",
        task_ticket: component.value.currentExecution.task_ticket,
      },
      {
        success(response, target) {},
      }
    );
  }
}

function beforeAddItemHook() {
  let currentItem = component.value.currentItem;
  let param = JSON.parse(currentItem.task_parameters);
  if (
    currentItem.dataset_configuration_id &&
    currentItem.dataset_configuration_id !== ""
  ) {
    param.dataset_configuration_id = currentItem.dataset_configuration_id;
  }
  if (
    currentItem.model_configuration_id &&
    currentItem.model_configuration_id !== ""
  ) {
    param.model_configuration_id = currentItem.model_configuration_id;
  }
  if (
    currentItem.trainer_configuration_id &&
    currentItem.trainer_configuration_id !== ""
  ) {
    param.trainer_configuration_id = currentItem.trainer_configuration_id;
  }
  currentItem.task_parameters = JSON.stringify(param);
}

const taskExecutionApi = new Api<any>("/task_execution");

function getItemExecutionList(item: any) {
  taskExecutionApi.getRequest(
    {
      task_sheet_id: item.task_sheet_id,
    },
    {
      success(response, target) {
        component.value.currentExecutions = response.data;
      },
    }
  );
}

function initItem(item: any) {
  taskExecutionApi.postRequest(
    {
      act: "create",
      task_sheet_id: item.task_sheet_id,
    },
    {
      success(response, target) {
        getItemExecutionList(item);
      },
    }
  );
}

function executionWithItemTicket(item: any) {
  taskExecutionApi.postRequest(
    {
      act: "execute",
      task_ticket: item.task_ticket,
    },
    {
      success(response, target) {
        getItemExecutionList(component.value.currentItem);
      },
    }
  );
}

function executionWithItemDirectly(item: any) {
  taskSheetApi.postRequest(
    {
      act: "execute",
      task_sheet_id: item.task_sheet_id,
    },
    {
      success(response, target) {
        console.log(response.data);
      },
      final() {
        getItemExecutionList(item);
      },
    }
  );
}

function stopAExecution(item: any) {
  taskExecutionApi.postRequest(
    {
      act: "stop",
      task_ticket: item.task_ticket,
    },
    {
      success(response, target) {
        console.log(response.data);
      },
      final() {
        getItemExecutionList(item);
      },
    }
  );
}

taskExecutionApi.deleteItemExeConfig = {
  success(response, target) {
    getItemExecutionList(component.value.currentItem);
  },
};
function deleteAExecution(item: any) {
  taskExecutionApi.deleteItem(item);
}

const taskExecutionResultApi = new Api<any>("/task_execution_result");

stateUpdateMap.set("TASK_EXE_RESULT_UPDATE", (data: any) => {
  component.value.currentExecutionResultList = data.result;
  for (const task_execution_result of component.value
    .currentExecutionResultList!) {
    if (task_execution_result.task_execution_presentation) {
      // console.log(task_execution_result.task_execution_presentation);
      for (let obj of task_execution_result.task_execution_presentation)
        for (let key in obj) {
          if (typeof obj[key] === "string" || typeof obj[key] === "boolean") {
            const numValue = Number(Number(obj[key]).toFixed(4));
            obj[key] = numValue;
          }
        }
    }
  }
});

function getItemExecutionResult(itemExecution: any) {
  taskExecutionResultApi.getRequest(
    {
      act: "start_ws_stream",
      task_ticket: itemExecution.task_ticket,
    },
    {
      success(response, target) {},
    }
  );
}

onUnmounted(() => {
  stateUpdateMap.clear();
});
</script>

<style></style>
