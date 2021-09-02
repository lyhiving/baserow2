<template functional>
  <div class="grid-view__cell">
    <div class="grid-field grid-field-text">
      {{ props.field.error ? '' : props.value }}
    </div>
  </div>
</template>
