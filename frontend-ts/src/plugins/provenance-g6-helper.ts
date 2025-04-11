import { configuration_types } from "@/assets/constant/configuration-type";
import {
  BaseBehavior,
  CanvasEvent,
  Circle,
  ComboEvent,
  NodeEvent,
  type ElementDatum,
  type IEvent,
} from "@antv/g6";

const provenance_cluster_keys = [
  "configurations",
  "executors",
  "pipeline_executions",
  "pipeline_sheets",
  "task_executions",
  "task_sheets",
];

function mapping(node: any) {
  const new_edges = [];
  const attr = node.data;
  if (attr.node_type === "task_sheet") {
    for (const attr_key of Object.keys(attr)) {
      const attr_value = attr[attr_key];
      // link executor with task_sheet
      // if (attr_key.endsWith("_executor_id") && attr_value !== "undefined") {
      //   new_edges.push({
      //     id: `${node.id}-${attr_value}`,
      //     source: node.id,
      //     target: attr_value,
      //     label: "uses",
      //   });
      // }
      // if (attr_key === "previous_task_ticket" && attr_value !== "undefined") {
      //   new_edges.push({
      //     id: `${node.id}-${attr_value}`,
      //     source: node.id,
      //     target: attr_value,
      //     label: "uses",
      //   });
      // }
      if (attr_key.endsWith("_executor_id") && attr_value !== "undefined") {
        new_edges.push({
          id: `${node.id}-${attr_value}`,
          source: attr_value,
          target: node.id,
          label: "used",
        });
      }
      if (attr_key === "previous_task_ticket" && attr_value !== "undefined") {
        new_edges.push({
          id: `${node.id}-${attr_value}`,
          source: attr_value,
          target: node.id,
          label: "used",
        });
      }
    }

    // link configuration with task_sheet
    for (let configuration_type of configuration_types) {
      const config_id_key = `${configuration_type}_configuration_id`;
      const config_value = attr.task_parameters[config_id_key];

      if (config_value !== undefined) {
        // if (configuration_type === "dataset") {
        //   for (let v of config_value) {
        //     new_edges.push({
        //       id: `${node.id}-${v}`,
        //       source: node.id,
        //       target: v,
        //       label: "uses",
        //     });
        //   }
        // } else {
        //   new_edges.push({
        //     id: `${node.id}-${config_value}`,
        //     source: node.id,
        //     target: config_value,
        //     label: "uses",
        //   });
        // }
        if (configuration_type === "dataset") {
          for (let v of config_value) {
            new_edges.push({
              id: `${node.id}-${v}`,
              source: v,
              target: node.id,
              label: "used",
            });
          }
        } else {
          new_edges.push({
            id: `${node.id}-${config_value}`,
            source: config_value,
            target: node.id,
            label: "used",
          });
        }
      }
    }
  }

  // link task_execution with task_sheet
  if (attr.node_type === "task_execution") {
    new_edges.push({
      source: node.id,
      target: attr.task_sheet_id,
      label: "wasGeneratedBy",
    });
  }

  if (attr.node_type === "pipeline_sheet") {
    for (const attr_key of Object.keys(attr)) {
      const attr_value = attr[attr_key];
      // link pipeline_sheet with task_sheet
      if (attr_key.endsWith("task_sheet_id") && attr_value !== "undefined") {
        new_edges.push({
          id: `${node.id}-${attr_value}`,
          source: node.id,
          target: attr_value,
          label: "wasDerivedFrom",
        });
      }
    }
  }

  if (attr.node_type === "pipeline_execution") {
    new_edges.push({
      source: node.id,
      target: attr.pipeline_sheet_id,
      label: "wasGeneratedBy",
    });
    // pipeline execution and task execution
    for (let task_execution_ticket of attr.task_execution_tickets) {
      // new_edges.push({
      //   source: node.id,
      //   target: task_execution_ticket,
      //   label: "uses",
      // });
      new_edges.push({
        source: task_execution_ticket,
        target: node.id,
        label: "used",
      });
    }
  }

  // todo: pipeline links
  return new_edges;
}

class ClickNode extends BaseBehavior {
  currentSelectedNodeIds: Set<string>;
  currentSelectedEdgeIds: Set<string>;
  animation: boolean = false;
  // TODO: finished the rules
  path: Map<string, Map<string, string[]>> = new Map([
    [
      "training pipeline sheet",
      new Map([
        [
          "training pipeline execution",
          ["training task execution", "model evaluation task execution"],
        ],
        ["model evaluation task sheet", ["executor", "configuration"]],
        ["training task sheet", ["executor", "configuration"]],
        ["model evaluation task execution", ["model evaluation task sheet"]],
        ["training task execution", ["training task sheet"]],
      ]),
    ],
    [
      "training task execution",
      new Map([
        [
          "training pipeline execution",
          ["training pipeline sheet", "model evaluation task execution"],
        ],
        ["model evaluation task execution", ["model evaluation task sheet"]],
        [
          "training pipeline sheet",
          ["training task sheet", "model evaluation task sheet"],
        ],
        ["model evaluation task sheet", ["executor", "configuration"]],
        ["training task sheet", ["executor", "configuration"]],
      ]),
    ],
  ]);

  constructor(context: any, options: any) {
    super(context, options);

    const { graph } = this.context;

    this.currentSelectedNodeIds = new Set();
    this.currentSelectedEdgeIds = new Set();

    graph.on(NodeEvent.DBLCLICK, (event: any) => {
      this.clearStates();
      const t = event.target;

      // console.log(t);
      const node = graph.getElementData(t.id);
      const { visitedNode, visitedEdge } = this.recursiveVisit(
        node,
        node.id!,
        [node.id],
        new Set<string>(),
        new Set<string>()
      );

      visitedNode.forEach(
        this.currentSelectedNodeIds.add,
        this.currentSelectedNodeIds
      );

      visitedEdge.forEach(
        this.currentSelectedEdgeIds.add,
        this.currentSelectedEdgeIds
      );
      // console.log(visitedEdge);

      this.currentSelectedNodeIds.add(t.id);
      // console.log(graph.getRelatedEdgesData(t.id));
      const recordForSelect: any = {};
      const recordForNotSelect: any = {};
      const comboForSelect: any = {};
      const comboForSelectNoSelect: any = {};
      for (const node of graph.getData().nodes) {
        if (this.currentSelectedNodeIds.has(node.id)) {
          recordForSelect[node.id] = "r-select";
          comboForSelect[node.combo!] = "r-select";
        } else {
          recordForNotSelect[node.id] = "r-not-select";
        }
      }
      for (const combo of graph.getData().combos) {
        if (comboForSelect[combo.id] === undefined) {
          comboForSelectNoSelect[combo.id] = "r-not-select";
        }
      }

      graph.setElementState(recordForSelect, this.animation);
      graph.setElementState(recordForNotSelect, this.animation);

      graph.setElementState(comboForSelect, this.animation);
      graph.setElementState(comboForSelectNoSelect, this.animation);

      const recordForSelectEdge: any = {};
      const recordForNotSelectEdge: any = {};
      for (const edge of graph.getData().edges) {
        const edgeId = edge.id as string;
        if (this.currentSelectedEdgeIds.has(edgeId)) {
          recordForSelectEdge[edgeId] = "r-select";
        } else {
          recordForNotSelectEdge[edgeId] = "r-not-select";
        }
      }
      // console.log(recordForSelectEdge);

      graph.setElementState(recordForSelectEdge, this.animation);
      graph.setElementState(recordForNotSelectEdge, this.animation);
    });
    graph.on(NodeEvent.CLICK, (event: any) => {
      const t = event.target;
      const node = graph.getElementData(t.id);
      const states: any = {};
      if (options.activeNode.value !== undefined) {
        states[options.activeNode.value.id!] = [];
      }
      states[node.id!] = ["c-select"];
      graph.setElementState(states, this.animation);
      // no underscore here
      if ((node.combo! as string).endsWith("task sheet")) {
        const meter_map = this.getTaskExecutionEvaluation(node.id!);
        options.executionMeters.value = meter_map;
        // console.log(meter_map);
      }
      // no underscore here
      if ((node.combo! as string).endsWith("pipeline sheet")) {
        const edges = graph.getRelatedEdgesData(node.id!);
        const pipeline_executions = [];
        for (const edge of edges) {
          if (edge.label === "wasGeneratedBy") {
            pipeline_executions.push(graph.getElementData(edge.source).data);
          }
        }
        const meter_map = this.newMeterMap();
        for (const pipeline_execution of pipeline_executions) {
          const task_execution_tickets =
            pipeline_execution!.task_execution_tickets;

          for (const task_execution_ticket of task_execution_tickets as string[]) {
            const task_execution = graph.getElementData(
              task_execution_ticket
            ).data;
            this.getMetersByExecution(task_execution, meter_map);
          }
        }

        meter_map["pipeline_execution_count"] = pipeline_executions.length;
        options.executionMeters.value = meter_map;
      }
      delete node.data!["running_info"];

      for (let k of Object.keys(node.data!)) {
        if (node.data![k] === null) {
          delete node.data![k];
        }
      }
      options.activeNode.value = node;
    });
    graph.on(CanvasEvent.CLICK, (event) => {
      this.clearStates();
    });
  }

  getMetersByExecution(task_execution: any, meter_map: any) {
    if (task_execution !== undefined) {
      // console.log(task_execution);
      if (task_execution.task_status === "finished") {
        meter_map["task_execution_count"]++;
        const dur =
          (task_execution.end_time as number) -
          (task_execution.start_time as number);
        // console.log(dur);
        meter_map["duration"] += Math.round(dur);
      }
      if (
        task_execution.running_info !== undefined &&
        (task_execution.running_info as any).emission_info !== undefined
      ) {
        // console.log((task_execution.running_info as any).emission_info.emissions);
        meter_map["emissions"] += (
          task_execution.running_info as any
        ).emission_info.emissions;
        meter_map["energy_consumed"] += (
          task_execution.running_info as any
        ).emission_info.energy_consumed;
      }
    }
  }

  newMeterMap() {
    const meter_map: any = {
      task_execution_count: 0,
      duration: 0,
      emissions: 0,
      energy_consumed: 0,
    };
    return meter_map;
  }

  getTaskExecutionEvaluation(task_sheet_id: string) {
    if (task_sheet_id === undefined) {
      return [];
    }
    const { graph } = this.context;
    const meter_map = this.newMeterMap();
    for (let edge of graph.getRelatedEdgesData(task_sheet_id)) {
      if (edge.label === "wasGeneratedBy") {
        // console.log(edge);
        const task_execution = graph.getElementData(edge.source).data;
        this.getMetersByExecution(task_execution, meter_map);
      }
    }
    return meter_map;
  }

  clearStates() {
    const { graph } = this.context;
    const recordForClear: any = {};
    for (const node of graph.getData().nodes) {
      recordForClear[node.id] = [];
    }
    for (const edge of graph.getData().edges) {
      var edgeId = edge.id as string;
      recordForClear[edgeId] = [];
    }
    for (const combo of graph.getData().combos) {
      var comboId = combo.id as string;
      recordForClear[comboId] = [];
    }
    graph.setElementState(recordForClear, false);
    this.currentSelectedNodeIds.clear();
    this.currentSelectedEdgeIds.clear();
    if (this.options.activeNode.value) {
      this.options.activeNode.value.states = [];
      this.options.activeNode.value = undefined;
    }
  }

  isIn(currId: string, targetId: string) {
    return currId !== targetId;
  }

  getPermitPath(rootCombo: string, currentCombo: string) {
    return this.path.get(rootCombo)?.get(currentCombo);
  }

  recursiveVisit(
    rootNode: ElementDatum,
    rootId: string,
    toBevisited: any[],
    visitedNode: Set<string>,
    visitedEdge: Set<string>
  ) {
    const { graph } = this.context;
    // console.log(rootNode);
    // console.log(rootNode.combo);
    if (toBevisited.length > 0) {
      const currentId = toBevisited.shift();
      visitedNode.add(currentId);

      // console.log("");
      // console.log("");
      // console.log("+++++++++++++++");
      // console.log("current id", currentId);
      const currentEl = graph.getElementData(currentId);
      // console.log("current currentEl", currentEl);
      const edgesData = graph.getRelatedEdgesData(currentId);
      // console.log("current edgesData", edgesData);

      for (const edgeData of edgesData) {
        const edgeId = edgeData.id as string;
        const targetId = edgeData.target;
        const targetNode = graph.getElementData(targetId);
        const sourceId = edgeData.source;
        const sourceNode = graph.getElementData(sourceId);
        const label = edgeData.label;

        if (visitedEdge.has(edgeId)) {
          continue;
        }

        if (this.isIn(currentId, targetId)) {
          if (rootId === sourceId) {
            toBevisited.push(targetId);
            visitedEdge.add(edgeId);
          } else {
            // console.log("------");
            // console.log(rootId, currentId, targetId, sourceId);
            // console.log(
            //   "in",
            //   targetNode,
            //   // targetNode.data!.component_type,
            //   // "-",
            //   // targetNode.data!.node_type,
            //   "<-",
            //   sourceNode
            //   // sourceNode.data!.component_type,
            //   // "-",
            //   // sourceNode.data!.node_type
            // );
            const permit = this.getPermitPath(
              rootNode.combo as string,
              currentEl.combo as string
            );
            if (permit && permit.includes(targetNode.combo as string)) {
              visitedEdge.add(edgeId);
              toBevisited.push(targetId);
            }
          }
          // console.log(this.path.get(rootNode.combo as string));
        } else {
          if (rootId === targetId) {
            toBevisited.push(sourceId);
            visitedEdge.add(edgeId);
          } else {
            // console.log(
            //   "out",
            //   targetNode,
            //   // targetNode.data!.component_type,
            //   // "-",
            //   // targetNode.data!.node_type,
            //   "<-",
            //   sourceNode
            //   // sourceNode.data!.component_type,
            //   // "-",
            //   // sourceNode.data!.node_type
            // );
            const permit = this.getPermitPath(
              rootNode.combo as string,
              currentEl.combo as string
            );
            if (permit && permit.includes(sourceNode.combo as string)) {
              visitedEdge.add(edgeId);
              toBevisited.push(sourceId);
            }
          }
        }
      }

      this.recursiveVisit(
        rootNode,
        rootId,
        toBevisited,
        visitedNode,
        visitedEdge
      );
    }
    return { visitedNode, visitedEdge };
  }
}

class BreathingCircle extends Circle {
  onCreate() {
    // console.log(this);
    // console.log(this, this.style.size);
    // const halo = this.shapeMap.halo;
    // halo.animate([{ lineWidth: 0 }, { lineWidth: 20 }], {
    //   duration: 1000,
    //   iterations: Infinity,
    //   direction: "alternate",
    // });
    this.animate([{ size: 200 }, { size: 250 }], {
      duration: 700,
      iterations: Infinity,
      direction: "alternate",
    });
  }
}

export { provenance_cluster_keys, mapping, ClickNode, BreathingCircle };
