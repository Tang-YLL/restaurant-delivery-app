// Element Plus组件库的全局注册配置
import { h } from 'vue'

// 简单的Element Plus组件模拟
export const ElCard = {
  name: 'ElCard',
  props: ['shadow', 'bodyStyle'],
  setup(props: any, { slots }: any) {
    return () => (
      <div class="el-card">
        {slots.header?.()}
        {slots.default?.()}
      </div>
    )
  },
}

export const ElRow = {
  name: 'ElRow',
  props: ['gutter'],
  setup(props: any, { slots }: any) {
    return () => <div class="el-row">{slots.default?.()}</div>
  },
}

export const ElCol = {
  name: 'ElCol',
  props: ['span', 'offset'],
  setup(props: any, { slots }: any) {
    return () => <div class="el-col">{slots.default?.()}</div>
  },
}

export const ElButton = {
  name: 'ElButton',
  props: ['type', 'size', 'loading', 'disabled', 'link'],
  emits: ['click'],
  setup(props: any, { emit, slots }: any) {
    return () => (
      <button
        class={`el-button el-button--${props.type || 'default'}`}
        disabled={props.disabled || props.loading}
        onClick={() => emit('click')}
      >
        {props.loading && <span>loading...</span>}
        {slots.default?.()}
      </button>
    )
  },
}

export const ElInput = {
  name: 'ElInput',
  props: ['modelValue', 'placeholder', 'type', 'size', 'showPassword'],
  emits: ['update:modelValue', 'keyup.enter'],
  setup(props: any, { emit, slots }: any) {
    return () => (
      <input
        type={props.type || 'text'}
        value={props.modelValue}
        placeholder={props.placeholder}
        onInput={(e: any) => emit('update:modelValue', e.target.value)}
        onKeyup={(e: any) => {
          if (e.key === 'Enter') emit('keyup.enter')
        }}
      />
    )
  },
}

export const ElForm = {
  name: 'ElForm',
  props: ['model', 'rules', 'inline', 'labelWidth'],
  setup(props: any, { slots }: any) {
    return () => <form>{slots.default?.()}</form>
  },
}

export const ElFormItem = {
  name: 'ElFormItem',
  props: ['prop', 'label', 'size'],
  setup(props: any, { slots }: any) {
    return () => <div class="el-form-item">{slots.default?.()}</div>
  },
}

export const ElIcon = {
  name: 'ElIcon',
  props: ['size'],
  setup(props: any, { slots }: any) {
    return () => <span class="el-icon">{slots.default?.()}</span>
  },
}

export const ElTable = {
  name: 'ElTable',
  props: ['data', 'border', 'stripe', 'vLoading'],
  setup(props: any, { slots }: any) {
    return () => <table class="el-table">{slots.default?.()}</table>
  },
}

export const ElTableColumn = {
  name: 'ElTableColumn',
  props: ['prop', 'label', 'width', 'fixed'],
  setup(props: any, { slots }: any) {
    return () => <th>{slots.default?.()}</th>
  },
}

export const ElTag = {
  name: 'ElTag',
  props: ['type', 'effect'],
  setup(props: any, { slots }: any) {
    return () => <span class={`el-tag el-tag--${props.type}`}>{slots.default?.()}</span>
  },
}

export const ElDropdown = {
  name: 'ElDropdown',
  props: [],
  emits: ['command'],
  setup(props: any, { emit, slots }: any) {
    return () => <div class="el-dropdown">{slots.default?.()}</div>
  },
}

export const ElDropdownMenu = {
  name: 'ElDropdownMenu',
  setup(props: any, { slots }: any) {
    return () => <div>{slots.default?.()}</div>
  },
}

export const ElDropdownItem = {
  name: 'ElDropdownItem',
  props: ['command'],
  setup(props: any, { slots }: any) {
    return () => <div>{slots.default?.()}</div>
  },
}

export const ElSelect = {
  name: 'ElSelect',
  props: ['modelValue', 'placeholder', 'clearable'],
  emits: ['update:modelValue'],
  setup(props: any, { emit, slots }: any) {
    return () => <select>{slots.default?.()}</select>
  },
}

export const ElOption = {
  name: 'ElOption',
  props: ['label', 'value'],
  setup(props: any) {
    return () => <option value={props.value}>{props.label}</option>
  },
}

export const ElDatePicker = {
  name: 'ElDatePicker',
  props: ['modelValue', 'type', 'rangeSeparator', 'startPlaceholder', 'endPlaceholder', 'valueFormat'],
  emits: ['update:modelValue'],
  setup(props: any, { emit }) {
    return () => <input type="text" placeholder="date picker" />
  },
}

export const ElPagination = {
  name: 'ElPagination',
  props: [
    'currentPage',
    'pageSize',
    'pageSizes',
    'total',
    'layout',
    'modelValue',
    'modelPageSize',
  ],
  emits: ['size-change', 'current-change', 'update:currentPage', 'update:pageSize'],
  setup(props: any, { emit }) {
    return () => <div class="el-pagination">Pagination</div>
  },
}

export const ElRadioGroup = {
  name: 'ElRadioGroup',
  props: ['modelValue'],
  emits: ['update:modelValue', 'change'],
  setup(props: any, { emit, slots }: any) {
    return () => <div>{slots.default?.()}</div>
  },
}

export const ElRadioButton = {
  name: 'ElRadioButton',
  props: ['label'],
  setup(props: any, { slots }: any) {
    return () => <button>{slots.default?.()}</button>
  },
}

export const ElMessageBox = {
  confirm: () => Promise.resolve(),
}
