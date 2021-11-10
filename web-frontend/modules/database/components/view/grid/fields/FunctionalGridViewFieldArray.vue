<template functional>
  <div class="grid-view__cell grid-field-many-to-many__cell">
    <div class="grid-field-many-to-many__list">
      <template v-if="props.field.array_formula_type === 'boolean'">
        <div
          v-for="(item, index) in props.value"
          :key="index"
          class="grid-field-boolean"
        >
          <div
            class="
              grid-field-boolean__checkbox
              grid-field-boolean__checkbox--read-only
            "
          >
            <i v-if="item.value === 'true'" class="fas fa-check"></i>
            <i
              v-else
              class="fas fa-times grid-field-boolean__checkbox__cross"
            ></i>
          </div></div
      ></template>
      <template v-else>
        <div
          v-for="(item, index) in props.value"
          :key="index"
          class="grid-field-many-to-many__item"
        >
          <span class="grid-field-many-to-many__name">
            {{ item.value }}
          </span>
        </div>
      </template>
    </div>
  </div>
</template>
