type Props<T> = { value: T; render: (value: T) => JSX.Element };

export interface ViewProps {
    title: string;
}

export function View({ title }: ViewProps): JSX.Element {
    return <h1>{title}</h1>;
}

export const Box = <T,>({ value, render }: Props<T>): JSX.Element => {
    return <div>{render(value)}</div>;
};
