import { Accordion, AccordionItem, TextInput } from "@carbon/react";
import styles from "./QnA.module.scss";
import React, { useState } from "react";

interface QnAItem {
  question: string;
  answer: string;
}

interface QnAProps {
  qna: QnAItem[];
}

const QnA: React.FC<QnAProps> = ({ qna }) => {
  const [feedbacks, setFeedbacks] = useState<{ [key: string]: string }>({});
  const hasAnswer = (item: QnAItem) => {
    return !item.answer.includes(
      "The answer cannot be determined from the provided context.",
    );
  };
  const itemTitle = (item: QnAItem) => {
    return (
      <div className={styles.question}>
        {hasAnswer(item) ? <span>✅ </span> : null}
        {item.question}
      </div>
    );
  };

  const itemContent = (item: QnAItem) => {
    return (
      <div>
        <div className={styles.answer}>{item.answer}</div>
        <TextInput
          id={`feedback-${item.question}`}
          labelText=""
          placeholder="Leave feedback here..."
          value={feedbacks[item.question] || ""}
          onChange={(e) =>
            setFeedbacks((prev) => ({
              ...prev,
              [item.question]: e.target.value,
            }))
          }
          style={{ marginTop: "1rem", width: "100%" }}
          size="lg"
        />
      </div>
    );
  };

  return (
    <div className={styles.qna_container}>
      <Accordion>
        {qna.map((item, index) => (
          <AccordionItem key={index} title={itemTitle(item)}>
            {itemContent(item)}
          </AccordionItem>
        ))}
      </Accordion>
    </div>
  );
};

export default QnA;
