import React from "react";

export function Card({ title, children }) {
    return <section className="card"><h2>{title}</h2>{children}</section>;
}

export const Badge = ({ label }) => {
    return <span>{label}</span>;
};
