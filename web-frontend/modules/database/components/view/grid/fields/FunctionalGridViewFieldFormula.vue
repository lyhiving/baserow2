<template functional>
  <div
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
