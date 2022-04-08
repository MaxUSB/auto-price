import {IDictionary} from "../../utils/types";
import React, {ReactNode, ChangeEvent} from 'react';
import {Grid, Autocomplete, TextField, createFilterOptions, MenuItem} from "@mui/material";

export type THandleChange = (item: string) => (event: ChangeEvent<HTMLInputElement>, customValue?: any) => void;

export interface ISelectOption {
  label: string | number;
  value: string | number;
  inputValue?: string;
}

export interface IFormItem {
  elementType: 'autocomplete' | 'select' | 'text';
  label: string;
  field: string;
  selectOptions?: ISelectOption[];
  groupBy?: boolean;
}

export type TGetFormElements = (
  item: IFormItem,
  data: any,
  handleChange: THandleChange,
) => ReactNode;

const getValue: any = (data: any, item: IFormItem) => data[item.field];

const formElements: IDictionary<TGetFormElements> = {
  autocomplete: (item: IFormItem, data: any, handleChange: THandleChange): ReactNode => {
    const filter = createFilterOptions<ISelectOption>();
    return (
      <Grid item xs={3} key={item.field}>
        <Autocomplete
          value={getValue(data, item)}
          options={item.selectOptions!.sort((a, b) => {
            if (a.label > b.label) return 1;
            if (a.label < b.label) return -1;
            return 0;
          })}
          groupBy={item.groupBy ? option => option.label[0].toUpperCase() : undefined}
          onChange={(event, newValue) => {
            const handler = handleChange(item.field);
            if (newValue) {
              if (newValue.inputValue) {
                handler({} as ChangeEvent<HTMLInputElement>, newValue.inputValue);
              } else {
                handler({} as ChangeEvent<HTMLInputElement>, newValue.value);
              }
            } else {
              handler({} as ChangeEvent<HTMLInputElement>, undefined);
            }
          }}
          filterOptions={(options, params) => {
            const filtered = filter(options, params);
            const {inputValue} = params;
            const isExisting = options.some(option => inputValue === option.label);
            if (inputValue !== '' && !isExisting) {
              filtered.push({
                inputValue,
                label: `Добавить '${inputValue}'`,
                value: inputValue,
              });
            }
            return filtered;
          }}
          getOptionLabel={option => {
            if (option.inputValue) {
              return option.inputValue;
            }
            return option.label;
          }}
          renderOption={(props, option) => <li {...props}>{option.label}</li>}
          renderInput={params => (<TextField required {...params} label={item.label}/>)}
          freeSolo
        />
      </Grid>
    );
  },
  select: (
    item: IFormItem,
    data: any,
    handleChange: THandleChange,
  ): ReactNode => (
    <Grid item xs={3} key={item.field}>
      <TextField
        required
        select
        label={item.label}
        value={getValue(data, item)}
        onChange={handleChange(item.field)}
        variant="outlined"
      >
        {item.selectOptions!.map(option => (
          <MenuItem value={option.value} key={option.value}>{option.label}</MenuItem>
        ))}
      </TextField>
    </Grid>
  ),
  text: (
    item: IFormItem,
    data: any,
    handleChange: THandleChange,
  ): ReactNode => (
    <Grid item xs={3} key={item.field}>
      <TextField
        required
        label={item.label}
        value={getValue(data, item)}
        onChange={handleChange(item.field)}
        variant="outlined"
      />
    </Grid>
  ),
};

const formGenerator = (
  items: IFormItem[],
  data: any,
  handleChange: THandleChange,
): ReactNode[] => items.map((item: IFormItem) => (
  formElements[item.elementType](
    item,
    data,
    handleChange,
  )
));

export default formGenerator;
