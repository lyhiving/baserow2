<template>
  <div>
    <div class="control__label">Example payload</div>
    <div class="control__elements">
      <div class="webhook__code-container">
        <div class="webhook__code-dropdown">
          <Dropdown v-model="selectedEvent" class="dropdown--floating-left">
            <DropdownItem
              name="When a row is created"
              value="rowCreated"
            ></DropdownItem>
            <DropdownItem
              name="When a row is updated"
              value="rowUpdated"
            ></DropdownItem>
            <DropdownItem
              name="When a row is deleted"
              value="rowDeleted"
            ></DropdownItem>
          </Dropdown>
        </div>
        <pre
          class="webhook__code"
        ><code>{{ JSON.stringify(getResponseExample(), null, 4)}}</code></pre>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
export default {
  name: 'WebhookExample',
  props: {
    userFieldNames: {
      type: Boolean,
      required: true,
      default: true,
    },
  },
  data() {
    return {
      events: {
        rowCreated: {
          table_id: 1,
          row_id: 1,
          event_type: 'row.created',
        },
        rowUpdated: {
          table_id: 1,
          row_id: 1,
          event_type: 'row.updated',
        },
        rowDeleted: {
          table_id: 1,
          row_id: 1,
          event_type: 'row.deleted',
        },
      },
      selectedEvent: 'rowCreated',
    }
  },
  computed: mapGetters({
    fields: 'field/getAllWithPrimary',
  }),
  methods: {
    getResponseExample() {
      const base = this.events[this.selectedEvent]
      const response = this.getResponseItem()
      let items = {}
      switch (this.selectedEvent) {
        case 'rowCreated':
          items = { values: response }
          break
        case 'rowUpdated':
          items = { values: response, old_values: response }
          break
        case 'rowDeleted':
          items = { values: {} }
          break
        default:
          items = { values: {} }
      }
      return { ...base, ...items }
    },
    getResponseItem() {
      const responseBase = { id: 0, order: '1.00000000000000000000' }
      const items = {}
      this.fields.forEach((field) => {
        const fieldType = this.$registry.get('field', field.type)
        const example = fieldType.getDocsResponseExample(field)
        if (this.$props.userFieldNames) {
          items[field.name] = example
        } else {
          items[`field_${field.id}`] = example
        }
      })
      return { ...responseBase, ...items }
    },
  },
}
</script>
