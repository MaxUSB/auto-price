import {IDictionary} from "../../utils/types";
import React, {ReactNode} from 'react';
import {Grid, Autocomplete, TextField, createFilterOptions, MenuItem} from "@mui/material";

export type THandleChange = (item: string, value: any) => void;

export interface ISelectOption {
  label: string;
  value: string;
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
  classes: any,
) => ReactNode;

const getValue: any = (data: any, item: IFormItem) => data[item.field] || '';

const formElements: IDictionary<TGetFormElements> = {
  autocomplete: (
    item: IFormItem,
    data: any,
    handleChange: THandleChange,
    classes: any,
  ): ReactNode => {
    const filter = createFilterOptions<ISelectOption>();
    return (
      <Grid item xs={12} md={6} key={item.field} className={classes.formItemContainer}>
        <Autocomplete
          value={getValue(data, item)}
          options={item.selectOptions!.sort((a, b) => {
            if (a.label > b.label) return 1;
            if (a.label < b.label) return -1;
            return 0;
          })}
          groupBy={item.groupBy ? option => option.label[0].toUpperCase() : undefined}
          onChange={(event, value) =>
            handleChange(item.field, value ? (value.inputValue ? value.inputValue : value.value) : undefined)
          }
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
          getOptionLabel={option => typeof option === 'string' ? option : (option.inputValue ? option.inputValue : option.label)}
          renderOption={(props, option) => <li {...props}>{option.label}</li>}
          renderInput={params => (<TextField required {...params} label={item.label}/>)}
          freeSolo
          className={classes.formItem}
        />
      </Grid>
    );
  },
  select: (
    item: IFormItem,
    data: any,
    handleChange: THandleChange,
    classes: any,
  ): ReactNode => (
    <Grid item xs={12} md={6} key={item.field} className={classes.formItemContainer}>
      <TextField
        required
        select
        label={item.label}
        value={getValue(data, item)}
        onChange={event => handleChange(item.field, event.target.value)}
        variant="outlined"
        className={classes.formItem}
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
    classes: any,
  ): ReactNode => (
    <Grid item xs={12} md={6} key={item.field} className={classes.formItemContainer}>
      <TextField
        required
        label={item.label}
        value={getValue(data, item)}
        onChange={event => handleChange(item.field, event.target.value)}
        variant="outlined"
        className={classes.formItem}
      />
    </Grid>
  ),
};

const formGenerator = (
  items: IFormItem[],
  data: any,
  handleChange: THandleChange,
  classes: any,
): ReactNode[] => items.map((item: IFormItem) => (
  formElements[item.elementType](
    item,
    data,
    handleChange,
    classes,
  )
));

export default formGenerator;
