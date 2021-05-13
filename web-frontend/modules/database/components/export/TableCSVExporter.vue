<template>
  <div>
    <div class="row">
      <div class="col col-4">
        <div class="control">
          <label class="control__label">Column separator</label>
          <div class="control__elements">
            <Dropdown
              v-model="localValue.csvColumnSeparator"
              :disabled="loading"
            >
              <DropdownItem name="," value="comma"></DropdownItem>
              <DropdownItem name=";" value="semi"></DropdownItem>
              <DropdownItem name="|" value="pipe"></DropdownItem>
              <DropdownItem name="<tab>" value="tab"></DropdownItem>
              <DropdownItem
                name="record separator (30)"
                value="record_separator"
              ></DropdownItem>
              <DropdownItem
                name="unit separator (31)"
                value="unit_separator"
              ></DropdownItem>
            </Dropdown>
          </div>
        </div>
      </div>
      <div class="col col-8">
        <div class="control">
          <label class="control__label">Encoding</label>
          <div class="control__elements">
            <Dropdown v-model="localValue.csvEncoding" :disabled="loading">
              <DropdownItem name="Unicode (UTF-8)" value="utf-8"></DropdownItem>
              <DropdownItem
                name="Arabic (ISO-8859-6)"
                value="iso-8859-6"
              ></DropdownItem>
              <DropdownItem
                name="Arabic (Windows-1256)"
                value="windows-1256"
              ></DropdownItem>
              <DropdownItem
                name="Baltic (ISO-8859-4)"
                value="iso-8859-4"
              ></DropdownItem>
              <DropdownItem
                name="Baltic (windows-1257)"
                value="windows-1257"
              ></DropdownItem>
              <DropdownItem
                name="Celtic (ISO-8859-14)"
                value="iso-8859-14"
              ></DropdownItem>
              <DropdownItem
                name="Central European (ISO-8859-2)"
                value="iso-8859-2"
              ></DropdownItem>
              <DropdownItem
                name="Central European (Windows-1250)"
                value="windows-1250"
              ></DropdownItem>
              <DropdownItem
                name="Chinese, Simplified (GBK)"
                value="gbk"
              ></DropdownItem>
              <DropdownItem
                name="Chinese (GB18030)"
                value="gb18030"
              ></DropdownItem>
              <DropdownItem
                name="Chinese Traditional (Big5)"
                value="big5"
              ></DropdownItem>
              <DropdownItem
                name="Cyrillic (KOI8-R)"
                value="koi8-r"
              ></DropdownItem>
              <DropdownItem
                name="Cyrillic (KOI8-U)"
                value="koi8-u"
              ></DropdownItem>
              <DropdownItem
                name="Cyrillic (ISO-8859-5)"
                value="iso-8859-5"
              ></DropdownItem>
              <DropdownItem
                name="Cyrillic (Windows-1251)"
                value="windows-1251"
              ></DropdownItem>
              <DropdownItem
                name="Cyrillic Mac OS (x-mac-cyrillic)"
                value="x-mac-cyrillic"
              ></DropdownItem>
              <DropdownItem
                name="Greek (ISO-8859-7)"
                value="iso-8859-7"
              ></DropdownItem>
              <DropdownItem
                name="Greek (Windows-1253)"
                value="windows-1253"
              ></DropdownItem>
              <DropdownItem
                name="Hebrew (ISO-8859-8)"
                value="iso-8859-8"
              ></DropdownItem>
              <DropdownItem
                name="Hebrew (Windows-1255)"
                value="windows-1255"
              ></DropdownItem>
              <DropdownItem
                name="Japanese (EUC-JP)"
                value="euc-jp"
              ></DropdownItem>
              <DropdownItem
                name="Japanese (ISO-2022-JP)"
                value="iso-2022-jp"
              ></DropdownItem>
              <DropdownItem
                name="Japanese (Shift-JIS)"
                value="shift-jis"
              ></DropdownItem>
              <DropdownItem
                name="Korean (EUC-KR)"
                value="euc-kr"
              ></DropdownItem>
              <DropdownItem name="Macintosh" value="macintosh"></DropdownItem>
              <DropdownItem
                name="Nordic (ISO-8859-10)"
                value="iso-8859-10"
              ></DropdownItem>
              <DropdownItem
                name="South-Eastern European (ISO-8859-16)"
                value="iso-8859-16"
              ></DropdownItem>
              <DropdownItem
                name="Thai (Windows-874)"
                value="windows-874"
              ></DropdownItem>
              <DropdownItem
                name="Turkish (Windows-1254)"
                value="windows-1254"
              ></DropdownItem>
              <DropdownItem
                name="Vietnamese (Windows-1258)"
                value="windows-1258"
              ></DropdownItem>
              <DropdownItem
                name="Western European (ISO-8859-1)"
                value="iso-8859-1"
              ></DropdownItem>
              <DropdownItem
                name="Western European (Windows-1252)"
                value="windows-1252"
              ></DropdownItem>
              <DropdownItem
                name="Latin 3 (ISO-8859-3)"
                value="iso-8859-3"
              ></DropdownItem>
            </Dropdown>
          </div>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col col-6">
        <div class="control">
          <label class="control__label">First row is header</label>
          <div class="control__elements">
            <Checkbox v-model="localValue.csvFirstRowHeader" :disabled="loading"
              >yes</Checkbox
            >
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TableCSVExporter',
  props: {
    value: {
      type: Object,
      required: true,
    },
    loading: {
      type: Boolean,
      required: true,
    },
  },
  data() {
    return {
      localValue: {
        csvFirstRowHeader: true,
        csvEncoding: 'utf-8',
        csvColumnSeparator: 'comma',
      },
    }
  },
  watch: {
    localValue: {
      handler(newVal) {
        this.$emit('input', newVal)
      },
      deep: true,
    },
  },
  created() {
    this.$emit('input', this.localValue)
  },
}
</script>
