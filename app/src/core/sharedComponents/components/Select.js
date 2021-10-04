import StyledSelect from "../styledComponents/StyledSelect";

const Select = () => {
    return (
        <div
            className="d-flex justify-content-center align-items center"
        >
            <StyledSelect
                className='justify-content-center align-items-center mt-2'    
            >
                <svg 
                    width="19" 
                    height="11" 
                    viewBox="0 0 19 11" 
                    fill="none" 
                    xmlns="http://www.w3.org/2000/svg">
                        <path 
                            d="M1 1L9.5 9.5L18 1" 
                            stroke="#195669" 
                            stroke-width="2" 
                            stroke-linecap="round"
                        />
                </svg>
            </StyledSelect>
        </div>
    )
}

export default Select;