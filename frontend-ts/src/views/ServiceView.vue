<template>
  <ComponentMgmt
    :component-id="id"
    title="Service"
    add-btn-text="Register"
    :item-viewable="false"
    :status-on-list="false"
    :component="component"
  >
    <template #itemAddForm>
      <v-row>
        <v-text-field
          label="Executor Name*"
          name="name"
          v-model="component.currentItem.executor_name"
          required
          density="compact"
          autocomplete="off"
        ></v-text-field>
      </v-row>
      <v-row>
        <v-text-field
          label="Executor Endpoint URL*"
          name="url"
          v-model="component.currentItem.executor_endpoint_url"
          required
          density="compact"
        ></v-text-field>
      </v-row>
      <v-row>
        <v-select
          label="Executor Type*"
          :items="executorTypeOptions"
          item-title="label"
          item-value="value"
          :rules="[(v) => !!v || 'Service type is required']"
          v-model="component.currentItem.executor_type"
          name="type"
          required
          density="compact"
          autocomplete="off"
        ></v-select>
      </v-row>
      <v-row>
        <v-textarea
          name="info"
          label="Executor Info"
          v-model="component.currentItem.executor_info"
          density="compact"
        ></v-textarea>
      </v-row>
    </template>
  </ComponentMgmt>
</template>

<script setup lang="ts">
import ComponentMgmt from "@/components/ComponentMgmt.vue";
import { ComponentTemplate } from "@/class/ComponentTemplate";
import { ref } from "vue";
import emitter from "@/plugins/emitter";
import type { ComponentAxiosExeConfig } from "@/plugins/api";
import Api from "@/plugins/api";

const id = "executor";
const executorTypeOptions: any[] = [
  { label: "Dataset", value: "dataset" },
  { label: "AI Model", value: "model" },
  { label: "XAI", value: "xai" },
  { label: "Model Evaluation", value: "model_evaluation" },
  { label: "XAI Evaluation", value: "xai_evaluation" },
];

const fetchItemListExeConfig: ComponentAxiosExeConfig<ComponentTemplate> = {
  success(response, target) {
    if (target) target.items = response.data;
  },
};

const addItemExeConfig: ComponentAxiosExeConfig<ComponentTemplate> = {
  success(response, target) {
    emitter.emit(`${id}-close-add-item-dialog`);
  },
};

const deleteItemExeConfig: ComponentAxiosExeConfig<ComponentTemplate> = {
  success(response, target) {
    emitter.emit(`${id}-close-add-item-dialog`);
  },
};

const api = new Api<ComponentTemplate>(
  "/executor",
  fetchItemListExeConfig,
  addItemExeConfig,
  deleteItemExeConfig
);

let component = ref<ComponentTemplate>(
  new ComponentTemplate(
    [
      {
        column: "ID",
        width: 3,
        key: "executor_id",
      },
      {
        column: "Name",
        width: 17,
        key: "executor_name",
      },
      // {
      //   column: "Endpoints",
      //   width: 8,
      //   key: "executor_endpoint_url",
      // },
      {
        column: "Executor Type",
        width: 25,
        key: "executor_type",
        render: (v) => {
          return v.replace("_", " ").toLocaleUpperCase();
        },
      },
      {
        column: "Code Base Hash-code",
        width: 15,
        key: "executor_info",
        render: (v: any) => {
          const hash = v.code_version_hash;
          return hash === undefined || hash === null
            ? "NaN"
            : hash.slice(0, 12);
        },
      },
      {
        column: "Status",
        width: 5,
        key: "executor_status",
        render: (v) => {
          return "online";
        },
      },
    ],
    api,
    () => {
      return { executor_info: "{}" };
    }
  )
);
</script>

<style></style>
