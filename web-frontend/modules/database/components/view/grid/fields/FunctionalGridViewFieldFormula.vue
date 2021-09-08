<template functional>
  <div
    v-tooltip="
      props.field.field_type === 'numeric' && props.value === 'NaN'
        ? 'Divide by zero error'
        : false
    "
    class="grid-view__cell"
    :class="{
      'cell-error':
        props.field.field_type === 'numeric' && props.value === 'NaN',
    }"
  >
    <div class="grid-field grid-field-text">
      {{ props.field.error ? '' : props.value }}
    </div>
  </div>
</template>
