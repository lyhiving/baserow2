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
        ><code>{{ JSON.stringify(events[selectedEvent], null, 4)}}</code></pre>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WebhookExample',
  data() {
    return {
      events: {
        rowCreated: {
          table_id: 1,
          row_id: 1,
          values: {
            Name: 'string',
            Price: 10.0,
            Comments: 'string',
          },
        },
        rowUpdated: {
          table_id: 1,
          row_id: 1,
          values: {
            Name: 'string',
            Price: 10.0,
            Comments: 'string',
          },
        },
        rowDeleted: {
          table_id: 1,
          row_id: 1,
          values: {},
        },
      },
      selectedEvent: 'rowCreated',
    }
  },
}
</script>
