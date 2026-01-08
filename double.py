import csv
import io
import streamlit as st

st.set_page_config(page_title="CSV Data Quoter", page_icon="🧾", layout="wide")

st.title("CSV Data Quoter")
st.write("Upload a CSV file to wrap all data cells (except header) with double quotes.")

uploaded = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded:
    try:
        # Read uploaded bytes into text
        text = uploaded.getvalue().decode("utf-8", errors="replace")
        input_buf = io.StringIO(text)
        reader = csv.reader(input_buf)

        rows = list(reader)
        if not rows:
            st.error("The uploaded file is empty.")
        else:
            header, data_rows = rows[0], rows[1:]
            
            st.info(f"📊 File loaded: {len(data_rows)} data rows found")

            # Prepare output buffer
            output_buf = io.StringIO()
            # Write header without forcing quotes
            output_buf.write(",".join(header) + "\n")
            
            # Show progress bar for large files
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Manually format each data row with single double quotes
            for idx, row in enumerate(data_rows):
                quoted_fields = []
                for field in row:
                    # Convert field to string
                    field_str = str(field)
                    # Remove ALL surrounding quotes (handle multiple layers like """, """, etc.)
                    while field_str.startswith('"') and field_str.endswith('"'):
                        field_str = field_str[1:-1]
                    # Escape any internal quotes by doubling them (CSV standard)
                    escaped_field = field_str.replace('"', '""')
                    # Wrap in single double quotes
                    quoted_fields.append(f'"{escaped_field}"')
                output_buf.write(",".join(quoted_fields) + "\n")
                
                # Update progress for large files
                if len(data_rows) > 100:
                    progress = (idx + 1) / len(data_rows)
                    progress_bar.progress(progress)
                    status_text.text(f"Processing row {idx + 1} of {len(data_rows)}...")

            result = output_buf.getvalue()
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()

            st.success(f"✅ Conversion complete! {len(data_rows)} rows processed.")
            
            # Show preview (first 10 lines for large files)
            preview_lines = result.split('\n')[:11]  # Header + 10 data rows
            preview_text = '\n'.join(preview_lines)
            if len(data_rows) > 10:
                preview_text += f"\n... ({len(data_rows) - 10} more rows)"
            
            st.subheader("Preview (first 10 rows):")
            st.text_area("Preview", preview_text, height=200, label_visibility="collapsed")

            # Download button
            st.download_button(
                label="📥 Download Quoted CSV",
                data=result.encode("utf-8"),
                file_name="quoted.csv",
                mime="text/csv",
                use_container_width=True
            )
            
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.exception(e)