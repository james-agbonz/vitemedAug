<template>
  <v-card class="mx-auto" style="height: 100%">
    <v-data-table
      :items="items"
      :headers="headers"
      return-object
      show-expand
      style="height: 100%"
      density="compact"
    >
      <template v-slot:top>
        <v-toolbar flat elevation="3" density="compact">
          <v-toolbar-title>Task Execution Emission Meters</v-toolbar-title>
        </v-toolbar>
      </template>
      <template v-slot:expanded-row="{ columns, item }">
        <tr>
          <td :colspan="columns.length" class="pt-3 pb-3">
            <v-card style="width: 100%" elevation="6">
              <v-card-text>
                <div style="display: inline-block; width: 50%">
                  <span style="font-weight: bold">CPU Energy (kWh): </span>
                  <span>{{
                    (
                      item as any
                    ).running_info.emission_info.cpu_energy.toExponential(4)
                  }}</span>
                </div>

                <div style="display: inline-block; width: 50%">
                  <span style="font-weight: bold">CPU Power (W): </span>
                  <span>{{
                    (
                      item as any
                    ).running_info.emission_info.cpu_power.toExponential(4)
                  }}</span>
                </div>
                <v-divider></v-divider>
                <div style="display: inline-block; width: 50%">
                  <span style="font-weight: bold">GPU Energy (kWh): </span>
                  <span>{{
                    (
                      item as any
                    ).running_info.emission_info.gpu_energy.toExponential(4)
                  }}</span>
                </div>

                <div style="display: inline-block; width: 50%">
                  <span style="font-weight: bold">GPU Power (W): </span>
                  <span>{{
                    (
                      item as any
                    ).running_info.emission_info.gpu_power.toExponential(4)
                  }}</span>
                </div>

                <v-divider></v-divider>

                <div style="display: inline-block; width: 50%">
                  <span style="font-weight: bold">RAM Energy (kWh): </span>
                  <span>{{
                    (
                      item as any
                    ).running_info.emission_info.ram_energy.toExponential(4)
                  }}</span>
                </div>
                <div style="display: inline-block; width: 50%">
                  <span style="font-weight: bold">RAM Power (W): </span>
                  <span>{{
                    (
                      item as any
                    ).running_info.emission_info.ram_power.toExponential(4)
                  }}</span>
                </div>
              </v-card-text>
            </v-card>
          </td>
        </tr>
      </template>
      <template v-slot:item.task_ticket="{ value }">
        {{ value.slice(0, 10) }}...
      </template>
      <template v-slot:item.task_status="{ value }">
        <div style="text-align: center">
          <ExecutionStatusIcon :task_status="value"></ExecutionStatusIcon>
        </div>
      </template>
      <template v-slot:header.task_status="{ column }">
        <div style="text-align: center">
          {{ column.title }}
        </div>
      </template>
    </v-data-table>
  </v-card>
</template>

<script setup lang="ts">
import ExecutionStatusIcon from "@/components/ExecutionStatusIcon.vue";

import Api from "@/plugins/api";
import { ax } from "@/plugins/axios-helper";
import { toTitleCase } from "@/plugins/global";
import { onMounted, ref } from "vue";
const { post, get } = ax();
const items = ref();
const taskExecutionApi = new Api<any>("/task_execution");

var headers = [
  {
    title: "Ticket",
    key: "task_ticket",
  },
  {
    title: "Status",
    key: "task_status",
  },
  {
    title: "Type",
    key: "task_type",
    value: (item: any) => toTitleCase(item.task_type),
  },
  {
    title: "CO₂eq (Kg)",
    key: "running_info.emission_info.emissions",
    value: (item: any) =>
      item.running_info.emission_info.emissions.toExponential(2),
  },
  {
    title: "Energy (kWh)",
    key: "running_info.emission_info.energy_consumed",
    value: (item: any) =>
      item.running_info.emission_info.energy_consumed.toExponential(2),
  },
  {
    title: "Country-region",
    key: "country-region",
    value: (item: any) =>
      `${item.running_info.emission_info.country_name} - ${toTitleCase(
        item.running_info.emission_info.region
      )}`,
  },
];

function getItemExecutionList() {
  taskExecutionApi.getRequest(
    {},
    {
      success(response, target) {
        const result = response.data.filter(
          (task_exe: any) =>
            task_exe.running_info !== undefined &&
            task_exe.running_info.emission_info !== undefined
        );
        // console.log(result);
        items.value = result;
      },
    }
  );
}

onMounted(() => {
  getItemExecutionList();
});
</script>

<style></style>
