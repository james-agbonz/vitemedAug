<template>
  <ComponentMgmt
    :ref="`${id}_component`"
    :component-id="id"
    title="Pipeline Sheet"
    add-btn-text="Add"
    :component="component"
    :item-viewable="true"
    :has-executions="true"
    :get-item-execution-list="getItemExecutionList"
    :init-item="initItem"
    :before-add-item-hook="beforeAddItemHook"
    :execution-with-item-ticket="executionWithItemTicket"
    :execution-with-item-directly="executionWithItemDirectly"
    :execution-result-dialog-active-hook="executionResultDialogActiveHook"
    :delete-a-execution="deleteAExecution"
    :stop-a-execution="stopAExecution"
    :get-item-execution-result="getItemExecutionResult"
    :status-on-list="true"
  >
    <template #itemAddForm>
      <v-row>
        <v-select
          label="Pipeline Type*"
          :items="pipeline_type_options"
          item-title="label"
          item-value="value"
          name="pipeline_type"
          v-model="component.currentItem.pipeline_type"
          required
          density="compact"
          autocomplete="off"
        ></v-select>
      </v-row>
      <v-row>
        <v-text-field
          label="Pipeline Sheet Name*"
          name="pipeline_sheet_name"
          v-model="component.currentItem.pipeline_sheet_name"
          required
          density="compact"
        ></v-text-field>
      </v-row>

      <v-row
        v-if="component.currentItem.pipeline_type === 'training_xai_pipeline'"
      >
        <v-col cols="10" offset="1">
          <v-slider
            :max="2"
            :ticks="training_xai_pipeline_reuse_level_list"
            v-model="training_xai_pipeline_reuse_level"
            show-ticks="always"
            step="1"
            tick-size="10"
          ></v-slider>
        </v-col>
      </v-row>

      <!-- training pipeline_execution-->
      <v-row
        v-if="
          component.currentItem.pipeline_type === 'training_xai_pipeline' &&
          training_xai_pipeline_reuse_level === 2
        "
      >
        <v-select
          label="Existing Training Pipeline Execution"
          :items="exist_training_pipeline_execution_list"
          item-title="pipeline_execution_name"
          item-value="pipeline_ticket"
          name="training_pipeline_execution_ticket"
          v-model="component.currentItem.train_task_sheet_id"
          ref="current_train_task_sheet_id"
          density="compact"
          autocomplete="off"
        ></v-select>
      </v-row>

      <!-- train task execution -->
      <v-row
        v-if="
          component.currentItem.pipeline_type !== 'training_xai_pipeline' ||
          training_xai_pipeline_reuse_level !== 2
        "
      >
        <v-select
          label="Train Task Sheet"
          :items="training_task_sheet_list"
          item-title="task_sheet_name"
          item-value="task_sheet_id"
          name="current_train_task_sheet_id"
          v-model="component.currentItem.train_task_sheet_id"
          ref="current_train_task_sheet_id"
          density="compact"
          autocomplete="off"
          multiple
        ></v-select>
      </v-row>

      <v-row
        v-if="
          component.currentItem.pipeline_type === 'xai_evaluation_pipeline' ||
          (component.currentItem.pipeline_type === 'training_xai_pipeline' &&
            training_xai_pipeline_reuse_level === 1)
        "
      >
        <v-col cols="4">
          <v-switch
            density="compact"
            label="Use Exist"
            color="warning"
            :disabled="component.currentItem.train_task_sheet_id === undefined"
            v-model="use_exist_train_execution"
          ></v-switch>
        </v-col>
        <v-col cols="8">
          <v-select
            label="Use Previous Model Train Executions"
            :items="exist_model_train_execution_list"
            item-title="task_execution_name"
            item-value="task_ticket"
            name="reused_train_task_execution_ticket"
            :disabled="!use_exist_train_execution"
            v-model="component.currentItem.reused_train_task_execution_ticket"
            density="compact"
            autocomplete="off"
          ></v-select>
        </v-col>
      </v-row>

      <!-- model eval -->
      <v-row
        v-if="
          ['training_pipeline', 'training_xai_pipeline'].includes(
            component.currentItem.pipeline_type
          ) && training_xai_pipeline_reuse_level !== 2
        "
      >
        <v-select
          label="Model Evaluation Task Sheet"
          :items="model_evaluation_task_sheet_list"
          item-title="task_sheet_name"
          item-value="task_sheet_id"
          name="current_model_evaluation_task_sheet_id"
          v-model="component.currentItem.model_evaluation_task_sheet_id"
          ref="current_model_evaluation_task_sheet_id"
          density="compact"
          autocomplete="off"
        ></v-select>
      </v-row>

      <!-- xai -->
      <v-row v-if="component.currentItem.pipeline_type !== 'training_pipeline'">
        <v-select
          label="XAI Task Sheet"
          :items="xai_task_sheet_list"
          item-title="task_sheet_name"
          item-value="task_sheet_id"
          name="current_xai_task_sheet_id"
          v-model="component.currentItem.xai_task_sheet_id"
          ref="current_xai_task_sheet_id"
          density="compact"
          autocomplete="off"
        ></v-select>
      </v-row>

      <!-- xai eval -->
      <v-row
        v-if="
          ['xai_evaluation_pipeline', 'training_xai_pipeline'].includes(
            component.currentItem.pipeline_type
          )
        "
      >
        <v-select
          label="XAI Evaluation Task Sheet"
          :items="xai_evaluation_task_sheet_list"
          item-title="task_sheet_name"
          item-value="task_sheet_id"
          name="current_evaluation_task_sheet_id"
          v-model="component.currentItem.xai_evaluation_task_sheet_id"
          ref="current_evaluation_task_sheet_id"
          density="compact"
          autocomplete="off"
        ></v-select>
      </v-row>
    </template>

    <template #itemForExecutions="{ item }">
      <td>{{ item.pipeline_ticket }}</td>
      <ExecutionStatus :task_status="item.training_task_status" />
      <ExecutionStatus :task_status="item.model_evaluation_task_status" />
      <ExecutionStatus :task_status="item.xai_task_status" />
      <ExecutionStatus :task_status="item.xai_evaluation_task_status" />
    </template>
  </ComponentMgmt>
</template>

<script setup lang="ts">
import ComponentMgmt from "@/components/ComponentMgmt.vue";
import { ComponentTemplate } from "@/class/ComponentTemplate";
import { onUnmounted, ref, watch } from "vue";
import emitter from "@/plugins/emitter";
import type { ComponentAxiosExeConfig } from "@/plugins/api";
import Api from "@/plugins/api";
import ExecutionStatus from "@/components/ExecutionStatus.vue";
import { getStateUpdateMap } from "@/plugins/global";

const id = "pipeline_sheet";
const pipeline_type_options: any[] = [
  { label: "Training Pipeline", value: "training_pipeline" },
  { label: "XAI Pipeline", value: "xai_pipeline" },
  { label: "XAI Evaluation Pipeline", value: "xai_evaluation_pipeline" },
  { label: "Training XAI Pipeline", value: "training_xai_pipeline" },
];

const training_xai_pipeline_reuse_level_list: any = {
  0: "No Reuse",
  1: "Reuse TT",
  2: "Reuse TP",
};

const training_xai_pipeline_reuse_level = ref<number>(0);

const pipeline_sheet_component = ref(null);

const xai_task_sheet_list = ref<any>([]);
const xai_evaluation_task_sheet_list = ref<any>([]);
const training_task_sheet_list = ref<any>([]);
const model_evaluation_task_sheet_list = ref<any>([]);

const use_exist_train_execution = ref<boolean>(false);
const exist_model_train_execution_list = ref<any>([]);
const exist_training_pipeline_execution_list = ref<any>([]);

const stateUpdateMap = getStateUpdateMap();

const pipelineSheetApi = new Api<ComponentTemplate>("/pipeline_sheet");

function beforeAddItemHook() {
  const pipeline_sheet_name = component.value.currentItem.pipeline_sheet_name;
  const pipeline_type = component.value.currentItem.pipeline_type;
  if (pipeline_sheet_name === undefined) {
    if (pipeline_type === "training_pipeline") {
      const model_evaluation_task_sheet_id =
        component.value.currentItem.model_evaluation_task_sheet_id;
      const model_evaluation_task_sheet =
        model_evaluation_task_sheet_list.value.find(
          (tts: any) => tts.task_sheet_id === model_evaluation_task_sheet_id
        );

      const training_task_sheet_ids =
        component.value.currentItem.train_task_sheet_id;
      // const training_task_sheet = training_task_sheet_list.value.find(
      //   (tts: any) => tts.task_sheet_id === training_task_sheet_id
      // );

      const training_task_sheets: any[] = [];
      const pipeline_sheet_names: string[] = [];

      for (const training_task_sheet_id of training_task_sheet_ids) {
        const currts = training_task_sheet_list.value.find(
          (tts: any) => tts.task_sheet_id === training_task_sheet_id
        );
        training_task_sheets.push(currts);
        pipeline_sheet_names.push(
          `${currts.task_sheet_name}-${model_evaluation_task_sheet.task_sheet_name}`
        );
      }

      component.value.currentItem.pipeline_sheet_name = pipeline_sheet_names;
    }
    if (pipeline_type === "xai_evaluation_pipeline") {
      const xai_task_sheet_id = component.value.currentItem.xai_task_sheet_id;
      const xai_task_sheet = xai_task_sheet_list.value.find(
        (tts: any) => tts.task_sheet_id === xai_task_sheet_id
      );
      const xai_evaluation_task_sheet_id =
        component.value.currentItem.xai_evaluation_task_sheet_id;
      const xai_evaluation_task_sheet =
        xai_evaluation_task_sheet_list.value.find(
          (tts: any) => tts.task_sheet_id === xai_evaluation_task_sheet_id
        );
      component.value.currentItem.pipeline_sheet_name = `${xai_task_sheet.task_sheet_name}-${xai_evaluation_task_sheet.task_sheet_name}`;
    }
  }
}

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
      //   width: 12,
      //   key: "pipeline_sheet_id",
      // },
      {
        column: "Name",
        width: 5,
        key: "pipeline_sheet_name",
      },
      {
        column: "Train TS. ID",
        width: 12,
        key: "train_task_sheet_id",
        render: (value) => (value ? value : "NaN"),
      },
      {
        column: "Model-Eval TS. ID",
        width: 12,
        key: "model_evaluation_task_sheet_id",
        render: (value) => (value ? value : "NaN"),
      },
      {
        column: "XAI TS. ID",
        width: 12,
        key: "xai_task_sheet_id",
        render: (value) => (value ? value : "NaN"),
      },
      {
        column: "XAI Eval TS. ID",
        width: 12,
        key: "xai_evaluation_task_sheet_id",
        render: (value) => (value ? value : "NaN"),
      },
    ],
    pipelineSheetApi,
    () => {
      return {
        pipeline_type: "training_pipeline",
      };
    }
  )
);

component.value.executionConfigs = [
  {
    column: "Pipeline Execution Ticket",
    width: 16,
    key: "pipeline_ticket",
  },
  {
    column: "Training",
    width: 12,
    key: "training_task_status",
    center: true,
  },
  {
    column: "Model-Eval",
    width: 15,
    key: "model_evaluation_task_status",
    center: true,
  },
  {
    column: "XAI",
    width: 10,
    key: "xai_task_status",
    center: true,
  },
  {
    column: "XAI-Eval",
    width: 14,
    key: "xai_evaluation_task_status",
    center: true,
  },
];

const taskSheetApi = new Api<ComponentTemplate>("/task_sheet", {
  success(response, target) {
    for (const sheet of response.data) {
      if (sheet.task_type === "xai") {
        xai_task_sheet_list.value.push(sheet);
      }
      if (sheet.task_type === "xai_evaluation") {
        xai_evaluation_task_sheet_list.value.push(sheet);
      }
      if (sheet.task_type === "training") {
        training_task_sheet_list.value.push(sheet);
      }
      if (sheet.task_type === "model_evaluation") {
        model_evaluation_task_sheet_list.value.push(sheet);
        // component.value.currentItem.model_evaluation_task_sheet_id =
        //   sheet.task_sheet_id;
      }
    }
  },
});

watch(
  () => [pipeline_sheet_component.value?.["addItemDialogActive"]],
  (nv, ov) => {
    if (pipeline_sheet_component.value?.["addItemDialogActive"]) {
      xai_task_sheet_list.value = [];
      xai_evaluation_task_sheet_list.value = [];
      training_task_sheet_list.value = [];
      model_evaluation_task_sheet_list.value = [];

      use_exist_train_execution.value = false;
      training_xai_pipeline_reuse_level.value = 0;
      exist_model_train_execution_list.value = [];
      exist_training_pipeline_execution_list.value = [];

      taskSheetApi.fetchItemsList();
    }
  }
);

watch(
  () => pipeline_sheet_component.value?.["executionDialogActive"],
  (open, ov) => {
    if (!open) {
      component.value.fetchItemsList();
    }
  }
);

const taskExecutionApi = new Api<any>("/task_execution");

watch(
  () => use_exist_train_execution.value,
  (n, o) => {
    if (n && component.value.currentItem.train_task_sheet_id) {
      taskExecutionApi.getRequest(
        {
          task_sheet_id: component.value.currentItem.train_task_sheet_id[0],
        },
        {
          success(response, target) {
            exist_model_train_execution_list.value = response.data;
          },
        }
      );
    } else {
      component.value.currentItem.reused_train_task_execution_ticket = null;
    }
  }
);

const pipelineExecutionApi = new Api<any>("/pipeline_execution");

function getItemExecutionList(item: any) {
  pipelineExecutionApi.getRequest(
    {
      pipeline_sheet_id: item.pipeline_sheet_id,
    },
    {
      success(response, target) {
        component.value.currentExecutions = response.data;
      },
    }
  );
}

stateUpdateMap.set("TASK_STATUS_UPDATE", (data: any) => {
  if (component.value.currentExecutions) {
    getItemExecutionList(component.value.currentItem);
  }
  if (!pipeline_sheet_component.value?.["executionDialogActive"]) {
    component.value.fetchItemsList();
  }
});

function initItem(item: any) {
  pipelineExecutionApi.postRequest(
    {
      act: "create",
      pipeline_sheet_id: item.pipeline_sheet_id,
    },
    {
      success(response, target) {
        getItemExecutionList(item);
        component.value.fetchItemsList();
      },
    }
  );
}

function executionWithItemTicket(item: any) {
  pipelineExecutionApi.postRequest(
    {
      act: "execute",
      pipeline_ticket: item.pipeline_ticket,
    },
    {
      success(response, target) {
        getItemExecutionList(component.value.currentItem);
      },
    }
  );
}

function executionWithItemDirectly(pipeline_sheet: any) {
  pipelineSheetApi.postRequest(
    {
      act: "execute",
      ...pipeline_sheet,
    },
    {
      success(response, target) {
        console.log(response.data);
      },
      final() {
        getItemExecutionList(pipeline_sheet);
      },
    }
  );
}

pipelineExecutionApi.deleteItemExeConfig = {
  success(response, target) {
    getItemExecutionList(component.value.currentItem);
  },
};
function deleteAExecution(item: any) {
  pipelineExecutionApi.deleteItem(item);
}

function stopAExecution(item: any) {
  pipelineExecutionApi.postRequest(
    {
      act: "stop",
      pipeline_ticket: item.pipeline_ticket,
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

const pipelineExecutionResultApi = new Api<any>("/pipeline_execution_result");

stateUpdateMap.set("PIPELINE_EXE_RESULT_UPDATE", (data: any) => {
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
  pipelineExecutionResultApi.getRequest(
    {
      act: "start_ws_stream",
      pipeline_ticket: itemExecution.pipeline_ticket,
    },
    {
      success(response, target) {},
    }
  );
}

function executionResultDialogActiveHook(ifOpen: boolean) {
  if (!ifOpen) {
    pipelineExecutionResultApi.getRequest(
      {
        act: "stop_ws_stream",
        pipeline_ticket: component.value.currentExecution.pipeline_ticket,
      },
      {
        success(response, target) {},
      }
    );
  }
}

onUnmounted(() => {});
</script>
