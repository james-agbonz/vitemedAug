import dayjs from "dayjs";

export function capitalizeFirstLetter(str: string) {
  if (str === null || str === undefined) return str;
  return str.charAt(0).toUpperCase() + str.slice(1);
}

export function toTitleCase(str: string) {
  return (
    str
      .replace(/_/g, " ")
      // .toLowerCase() // Convert the entire string to lowercase
      .split(" ") // Split the string into an array of words
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1)) // Capitalize the first letter of each word
      .join(" ")
  ); // Join the array back into a string
}

export function formatSeconds(seconds: number) {
  // Calculate hours, minutes and seconds
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  // Format to hh:mm:ss
  const formattedTime = [
    String(hours).padStart(2, "0"),
    String(minutes).padStart(2, "0"),
    String(secs).padStart(2, "0"),
  ].join(":");

  return formattedTime;
}

export function arrMapping(arr: string[], mapping_func: (v: string) => string) {
  const new_arr = [];
  for (let e of arr) {
    new_arr.push(mapping_func(e));
  }
  return new_arr;
}

export function timestampFormat(ts: number) {
  return dayjs.unix(ts).utc().local().format("HH:mm:ss, ddd, MMM-Do, YYYY ");
}

import { getCurrentInstance } from "vue";

export function getWs() {
  const app = getCurrentInstance()?.appContext.app;
  return app?.config.globalProperties.ws;
}

export function getStateUpdateMap(): Map<string, Function> {
  const app = getCurrentInstance()?.appContext.app;
  return app?.config.globalProperties.stateUpdateMap;
}
