<template>
  <v-card height="100%" density="compact">
    <template v-slot:title>
      <div class="clearfix">
        <div style="width: 50%; float: left; padding: 0.1em">
          {{ title }}
        </div>
        <div
          style="width: 50%; float: right; text-align: right; padding: 0.1em"
        >
          <v-btn size="small" color="success" @click="openAddItemDialog">
            {{ addBtnText }}
          </v-btn>
        </div>
      </div>
    </template>

    <v-divider></v-divider>

    <!-- item list -->
    <v-table density="compact" style="height: 94%; padding-bottom: 1em">
      <colgroup>
        <col
          v-for="item in component.configs"
          :key="item.column"
          :style="{
            width: `${item.width}%`,
          }"
        />
        <col v-if="statusOnList" span="1" style="width: 6%" />
        <col
          span="1"
          :style="{
            width: `${funcBtnColWidth - 10}%`,
          }"
        />
      </colgroup>
      <thead>
        <tr>
          <th
            class="text-left font-weight-bold"
            v-for="item in component.configs"
            :key="item.column"
          >
            {{ item.column }}
          </th>
          <th v-if="statusOnList" class="text-center font-weight-bold">
            Status
          </th>
          <th class="text-left font-weight-bold"></th>
        </tr>
      </thead>
      <tbody>
        <tr
          class="trHover"
          v-for="(item, itemIndex) in component.items"
          :key="item[component.itemKeyList[0]]"
        >
          <td v-for="ki in component.itemKeyList">
            {{ renderValue(ki, item[ki], itemIndex) }}
          </td>
          <ExecutionStatus
            v-if="statusOnList"
            :task_status="item.task_status"
          />
          <td style="text-align: right">
            <v-btn
              v-if="itemViewable"
              color="blue"
              size="x-small"
              prepend-icon="mdi-television"
              @click="viewItem(item)"
              >Detail</v-btn
            >
            <v-btn
              size="x-small"
              variant="outlined"
              style="margin-left: 0.5em"
              color="blue-darken-1"
              @click="initItem ? initItem(item) : console.log('no initItem')"
            >
              INIT
            </v-btn>
            <v-btn
              v-if="hasExecutions"
              style="margin-left: 0.5em"
              color="pink"
              size="x-small"
              prepend-icon="mdi-play"
              @click="
                executionWithItemDirectly
                  ? executionWithItemDirectly(item)
                  : console.log('no executionWithItemDirectly')
              "
              >Execute</v-btn
            >
            <v-btn
              v-if="hasExecutions"
              style="margin-left: 0.5em"
              color="success"
              size="x-small"
              prepend-icon="mdi-play"
              @click="viewItemExecutionList(item)"
              >Executions</v-btn
            >
            <v-btn
              style="margin-left: 0.5em"
              color="error"
              size="x-small"
              prepend-icon="mdi-delete"
              @click="component.deleteItem(item)"
              >Delete</v-btn
            >
          </td>
        </tr>
      </tbody>
    </v-table>

    <!-- add item dialog -->
    <v-dialog
      :id="`${componentId}-add-dialog`"
      contained
      v-model="addItemDialogActive"
      max-width="600px"
      class="add-dialog"
    >
      <!-- TODO: form validation -->
      <v-form
        :id="`${componentId}-add-form`"
        :ref="`${componentId}-add-form`"
        :readonly="addItemDisabled"
        lazy-validation
        @submit.prevent="(e) => addItem(e)"
      >
        <v-card density="compact">
          <v-card-title>
            <span class="text-h5">{{
              addItemDisabled ? `${title} Detail` : `New ${title}`
            }}</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <slot name="itemAddForm"> </slot>
            </v-container>
            <small>*indicates required field</small>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="red-darken-1" @click="closeAddItemDialog">
              Close
            </v-btn>
            <v-btn
              v-if="!addItemDisabled"
              type="submit"
              color="green-darken-1"
              :form="`${componentId}-add-form`"
            >
              Submit
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-form>
    </v-dialog>

    <!-- item executions list dialog -->
    <v-dialog
      :id="`${componentId}-executions-dialog`"
      style="height: 100%"
      contained
      v-model="executionDialogActive"
    >
      <v-card style="height: 100000px">
        <v-card-title>
          Executions for
          {{
            component.currentItem.pipeline_sheet_name
              ? "Pipeline Sheet"
              : "Task Sheet"
          }}:
        </v-card-title>
        <v-card-subtitle class="mb-3" style="font-weight: 900">
          {{
            component.currentItem.pipeline_sheet_name ||
            component.currentItem.task_sheet_name
          }}
        </v-card-subtitle>
        <v-divider></v-divider>

        <v-card-text>
          <v-table density="compact">
            <colgroup>
              <col
                v-for="item in component.executionConfigs"
                :key="item.column"
                :style="{
                  width: `${item.width}%`,
                }"
              />
              <col
                span="1"
                :style="{
                  width: `${funcBtnColWidthForExecution}%`,
                }"
              />
            </colgroup>
            <thead>
              <tr>
                <th
                  :class="{
                    'text-left': !item.center,
                    'text-center': item.center,
                    'font-weight-bold': true,
                  }"
                  v-for="item in component.executionConfigs"
                  :key="item.column"
                >
                  {{ item.column }}
                </th>
                <th class="text-left font-weight-bold"></th>
              </tr>
            </thead>
            <tbody>
              <tr
                class="trHover"
                v-for="item in component.currentExecutions"
                :key="item.task_ticket"
              >
                <slot name="itemForExecutions" :item="item"> </slot>

                <!-- function -->
                <td style="text-align: right">
                  <v-btn
                    size="x-small"
                    color="green-darken-1"
                    :disabled="item.task_status !== 'initialized'"
                    @click="
                      executionWithItemTicket
                        ? executionWithItemTicket(item)
                        : console.log('no executionWithItemTicket')
                    "
                  >
                    Execute
                  </v-btn>
                  <v-btn
                    style="margin-left: 0.5em"
                    color="blue"
                    size="x-small"
                    prepend-icon="mdi-clipboard-minus-outline"
                    @click="viewItemExecutionResult(item)"
                    >Result</v-btn
                  >
                  <v-btn
                    style="margin-left: 0.5em"
                    color="warning"
                    size="x-small"
                    prepend-icon="mdi-close"
                    :disabled="item.task_status !== 'running'"
                    @click="
                      stopAExecution
                        ? stopAExecution(item)
                        : console.log('no stopAExecution')
                    "
                    >Stop</v-btn
                  >
                  <v-btn
                    style="margin-left: 0.5em"
                    color="error"
                    size="x-small"
                    prepend-icon="mdi-delete"
                    @click="
                      deleteAExecution
                        ? deleteAExecution(item)
                        : console.log('no deleteAExecution')
                    "
                    :disabled="item.task_status === 'running'"
                    >Delete</v-btn
                  >
                </td>
              </tr>
            </tbody>
          </v-table>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>

          <v-btn
            size="small"
            variant="outlined"
            color="blue-darken-1"
            form="task-sheet-create-form"
            @click="
              initItem
                ? initItem(component.currentItem)
                : console.log('no initItem')
            "
          >
            INIT
          </v-btn>
          <v-btn
            size="small"
            variant="outlined"
            color="green-darken-1"
            form="task-sheet-create-form"
            @click="
              executionWithItemDirectly
                ? executionWithItemDirectly(component.currentItem)
                : console.log('no executionWithItemDirectly')
            "
          >
            Execute Directly
          </v-btn>
          <v-btn
            size="small"
            variant="outlined"
            color="red-darken-1"
            @click="executionDialogActive = false"
          >
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- item execution result dialog -->
    <v-dialog
      :id="`${componentId}-executions-result-dialog`"
      style="height: 100%; align-items: center"
      contained
      v-model="executionResultDialogActive"
      class="exe-result-dialog"
    >
      <v-card style="width: 95%" density="compact">
        <v-card-title>
          <v-card-actions>
            <span class="text-h5">
              {{
                component.currentItem.pipeline_sheet_name ? "Pipeline" : "Task"
              }}
              Execution Result</span
            >
            <v-spacer></v-spacer>

            <v-btn
              size="small"
              variant="outlined"
              color="red-darken-1"
              @click="executionResultDialogActive = false"
            >
              Close
            </v-btn>
          </v-card-actions>
        </v-card-title>
        <v-divider></v-divider>

        <v-container style="overflow: scroll" density="compact">
          <!-- Std out and error result -->
          <div
            v-for="(executionResult, i) in component.currentExecutionResultList"
            :key="i"
          >
            <v-card-title>
              <span class="text-h6"
                >Task output and error for: [{{
                  executionResult.task_execution_name
                }}]</span
              >
            </v-card-title>
            <v-card-text>
              <v-expansion-panels variant="popout" theme="dark">
                <v-expansion-panel>
                  <v-expansion-panel-title>
                    Standard Output
                  </v-expansion-panel-title>
                  <v-divider></v-divider>
                  <v-expansion-panel-text>
                    <p v-for="(text, i) in executionResult.std_out" :key="i">
                      {{ text.replaceAll(" ", "&nbsp;") }}
                    </p>
                  </v-expansion-panel-text>
                </v-expansion-panel>
                <v-expansion-panel>
                  <v-expansion-panel-title>
                    Standard Error
                  </v-expansion-panel-title>
                  <v-divider></v-divider>
                  <v-expansion-panel-text>
                    <p v-for="(text, i) in executionResult.std_err" :key="i">
                      {{ text.replaceAll(" ", "&nbsp;") }}
                    </p>
                  </v-expansion-panel-text>
                </v-expansion-panel>
                <v-expansion-panel
                  v-if="executionResult.task_execution_presentation"
                >
                  <v-expansion-panel-title>
                    Presentation
                  </v-expansion-panel-title>
                  <v-divider></v-divider>
                  <v-expansion-panel-text>
                    <v-data-table
                      density="compact"
                      hide-default-footer
                      :items="executionResult.task_execution_presentation"
                    ></v-data-table>
                  </v-expansion-panel-text>
                </v-expansion-panel>
              </v-expansion-panels>
            </v-card-text>
          </div>
        </v-container>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script setup lang="ts">
import { ComponentTemplate } from "@/class/ComponentTemplate";
import emitter from "@/plugins/emitter";
import { onMounted, onUnmounted, ref, watch } from "vue";
import ExecutionStatus from "@/components/ExecutionStatus.vue";

const addItemDialogActive = ref(false);
const executionDialogActive = ref(false);
const executionResultDialogActive = ref(false);

const addItemDisabled = ref(false);

const {
  title,
  component,
  componentId,
  beforeOpenAddItemDialogHook,
  beforeOpenViewItemDialogHook,
  executionResultDialogActiveHook,
  beforeAddItemHook,
  getItemExecutionList,
  initItem,
  executionWithItemTicket,
  executionWithItemDirectly,
  stopAExecution,
  deleteAExecution,
  getItemExecutionResult,
} = defineProps<{
  statusOnList: boolean;
  componentId: String;
  title: String;
  addBtnText: String;
  component: ComponentTemplate;
  itemViewable: boolean;
  hasExecutions?: boolean;
  beforeOpenAddItemDialogHook?: () => void;
  beforeOpenViewItemDialogHook?: (item: any) => void;
  executionResultDialogActiveHook?: (item: boolean) => void;
  beforeAddItemHook?: () => void;
  getItemExecutionList?: (item: any) => void;
  initItem?: (item: any) => void;
  executionWithItemTicket?: (item: any) => void;
  executionWithItemDirectly?: (item: any) => void;
  stopAExecution?: (item: any) => void;
  deleteAExecution?: (item: any) => void;
  getItemExecutionResult?: (item: any) => void;
}>();

let funcBtnColWidth = 100;
for (let cfg of component.configs) {
  funcBtnColWidth -= cfg.width;
}

let funcBtnColWidthForExecution = 100;
if (component.executionConfigs)
  for (let cfg of component.executionConfigs) {
    funcBtnColWidthForExecution -= cfg.width;
  }

watch(addItemDialogActive, (open, ov) => {
  if (!open) {
    addItemDisabled.value = false;
    component.clear();
  }
});

watch(executionDialogActive, (open, ov) => {
  if (!open) {
    component.clear();
  }
});

function addItem(event: SubmitEvent) {
  beforeAddItemHook ? beforeAddItemHook() : console.log("no beforeAddItemHook");
  component.addItem(event);
}

function openAddItemDialog() {
  beforeOpenAddItemDialogHook
    ? beforeOpenAddItemDialogHook()
    : console.log("no beforeOpenAddItemDialogHook");
  addItemDialogActive.value = true;
}

function closeAddItemDialog() {
  addItemDialogActive.value = false;
}

function viewItem(item: any) {
  // deep copy to prevent comtamination
  const newI = JSON.parse(JSON.stringify(item));
  beforeOpenViewItemDialogHook
    ? beforeOpenViewItemDialogHook(newI)
    : console.log("no getItemExecutionList");
  component.currentItem = newI;

  addItemDialogActive.value = true;
  addItemDisabled.value = true;
}

function viewItemExecutionList(item: any) {
  const newI = JSON.parse(JSON.stringify(item));
  component.currentItem = newI;
  executionDialogActive.value = true;
  getItemExecutionList
    ? getItemExecutionList(newI)
    : console.log("no getItemExecutionList");
}

function viewItemExecutionResult(itemExecution: any) {
  executionResultDialogActive.value = true;
  component.currentExecution = itemExecution;
  getItemExecutionResult
    ? getItemExecutionResult(itemExecution)
    : console.log("no getItemExecutionResult");
}

watch(executionResultDialogActive, (open, ov) => {
  executionResultDialogActiveHook
    ? executionResultDialogActiveHook(open)
    : console.log("no executionResultDialogActiveHook");
  if (!open) {
    component.currentExecutionResultList = [];
  }
});

function renderValue(ki: string, v: string, i: number) {
  const rf = component.columnValueRenderMap.get(ki);
  return rf ? rf(v, i) : v;
}

onMounted(() => {
  console.log("onMounted", componentId);
  emitter.on(`${componentId}-close-add-item-dialog`, (v: any) => {
    closeAddItemDialog();
    component.fetchItemsList();
  });
  component.fetchItemsList();
});
onUnmounted(() => {
  emitter.off(`${componentId}-close-add-item-dialog`);
});

defineExpose({
  addItemDialogActive,
  executionDialogActive,
});
</script>

<style>
.add-dialog > .v-overlay__content {
  right: 1em;
}

.exe-result-dialog > .v-overlay__content {
  align-items: center;
  max-height: 95%;
  /* height: 100%; */
}
.stt {
  text-align: center;
}
</style>
