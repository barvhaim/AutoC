import React, { useState } from "react";
import { useDispatch } from "react-redux";
import { Button, Form, InlineLoading, TextInput } from "@carbon/react";
import { Search } from "@carbon/icons-react";
import { analyze } from "../../service/analyze.ts";

import styles from "./SearchBanner.module.scss";
import { setAnalysisResults } from "../../store/analysisSlice.ts";

const SearchBanner = () => {
  const dispatch = useDispatch();
  const [url, setUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      setIsLoading(true);
      const response: any = await analyze(url);
      if (response.status === 200) {
        dispatch(
          setAnalysisResults({
            url: response.data?.url,
            keywords: response.data?.keywords_found,
            qna: response.data?.qna,
            iocs: response.data?.iocs_found,
            mitre_ttps: response.data?.mitre_ttps,
          }),
        );
      }
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.search_banner_container}>
      <div className={styles.search_banner_title}>🕵️‍♂️ Analyze blog post</div>
      <Form onSubmit={handleSubmit} className={styles.form_container}>
        <TextInput
          id={"url-input"}
          autoFocus={true}
          autoComplete={"off"}
          size={"md"}
          labelText={""}
          placeholder="https://example.com/blog-post"
          value={url}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
            setUrl(e.target.value)
          }
        />
        <Button
          size={"md"}
          renderIcon={Search}
          kind={"primary"}
          disabled={isLoading || !url.trim()}
          type={"submit"}
        >
          Analyze
        </Button>
      </Form>

      {isLoading && (
        <div>
          <InlineLoading
            status={"active"}
            description={"Please wait while we analyze the blog..."}
          />
        </div>
      )}
    </div>
  );
};

export default SearchBanner;
