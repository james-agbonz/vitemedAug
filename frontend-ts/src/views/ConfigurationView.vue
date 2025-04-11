<template>
  <ComponentMgmt
    :component-id="id"
    title="Configuration"
    add-btn-text="Add"
    :component="component"
    :item-viewable="true"
    :status-on-list="false"
  >
    <template #itemAddForm>
      <v-row>
        <v-text-field
          label="Configuration Name*"
          name="name"
          v-model="component.currentItem.configuration_name"
          required
          density="compact"
        ></v-text-field>
      </v-row>
      <v-row>
        <v-select
          label="Configuration Type*"
          :items="configuration_types"
          item-title="label"
          item-value="value"
          v-model="component.currentItem.configuration_type"
          name="configuration_type"
          required
          density="compact"
          autocomplete="off"
        ></v-select>
      </v-row>
      <v-row>
        <v-textarea
          label="Configuration Content"
          name="configuration_content"
          v-model="component.currentItem.configuration_content"
          density="compact"
          rows="10"
        ></v-textarea>
      </v-row>
    </template>
  </ComponentMgmt>
</template>

<script setup lang="ts">
import ComponentMgmt from "@/components/ComponentMgmt.vue";
import { ComponentTemplate } from "@/class/ComponentTemplate";
import { ref } from "vue";
import { capitalizeFirstLetter } from "@/plugins/global";
import emitter from "@/plugins/emitter";
import type { ComponentAxiosExeConfig } from "@/plugins/api";
import Api from "@/plugins/api";

const id = "configuration";
const configuration_types = [
  {
    label: "Dataset",
    value: "dataset",
  },
  { label: "Model", value: "model" },
  { label: "Trainer", value: "trainer" },
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
  "/configuration",
  fetchItemListExeConfig,
  addItemExeConfig,
  deleteItemExeConfig
);

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
      //   width: 20,
      //   key: "configuration_id",
      // },
      {
        column: "Name",
        width: 10,
        key: "configuration_name",
      },
      {
        column: "Configuration Type",
        width: 20,
        key: "configuration_type",
        render: (v) => {
          return capitalizeFirstLetter(v);
        },
      },
    ],
    api,
    () => {
      return {};
    }
  )
);
</script>

<style></style>
